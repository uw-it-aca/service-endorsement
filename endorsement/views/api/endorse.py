# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from userservice.user import UserService
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model, get_endorsee_email_model)
from endorsement.services import endorsement_services, is_valid_endorser
from endorsement.dao.pws import get_person
from endorsement.dao.endorse import get_endorsements_for_endorsee
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.util.auth import is_admin_user
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import (
    InvalidNetID, UnrecognizedUWNetid, NoEndorsementException,
    CategoryFailureException, SubscriptionFailureException,
    MissingReasonException)


logger = logging.getLogger(__name__)


class Endorse(RESTDispatch):
    """
    Endorse provided endorsee list
    """
    def post(self, request, *args, **kwargs):
        endorsees = request.data.get('endorsees', {})
        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            return invalid_session(logger)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger)

        original_user = user_service.get_original_user()
        acted_as = None if (netid == original_user) else original_user
        if acted_as and not is_admin_user(request):
            return invalid_endorser(logger)

        endorser = get_endorser_model(netid)
        endorser_json = endorser.json_data()
        endorser_pws = get_person(netid)
        active_services = set()

        endorsed = {
            'endorser': endorser_json,
            'endorser_name': endorser_pws.display_name,
            'endorser_email': endorser_pws.email_addresses[0] if (
                len(endorser_pws.email_addresses) > 0) else None,
            'endorsed': {}
        }

        for endorsee_netid, to_endorse in endorsees.items():
            try:
                endorsee = get_endorsee_model(endorsee_netid)
                endorsements = {
                    'name': endorsee.display_name,
                    'is_person': endorsee.is_person,
                    'endorsements': {}
                }

                if 'email' in to_endorse:
                    endorsements['email'] = get_endorsee_email_model(
                        endorsee, endorser, email=to_endorse['email']).email

                for service in endorsement_services():
                    if service.service_name in to_endorse:
                        if (service.valid_endorser(endorser.netid)
                                and service.valid_endorsee(
                                    endorsee, endorser)):
                            self._endorse(to_endorse, service,
                                          endorser, endorser_json,
                                          endorsee, acted_as,
                                          endorsements['endorsements'])

                            active_services.add(service.service_name)
                        else:
                            err = 'Shared netid {} not allowed for {}'.format(
                                endorsee.netid, service.category_name)
                            endorsements['endorsements'][
                                service.service_name] = {
                                    'endorsee': endorsee.json_data(),
                                    'error': err
                                }
            except InvalidNetID as ex:
                endorsements = {
                    'endorsee': {
                        'netid': endorsee_netid
                    },
                    'name': "",
                    'error': "Invalid NetID".format(endorsee_netid)
                }
            except (KeyError, UnrecognizedUWNetid) as ex:
                endorsements = {
                    'error': '{0}'.format(ex)
                }

                if 'endorsee' in locals():
                    endorsements['endorsee'] = endorsee.json_data()
                    endorsements['name'] = endorsee.display_name
                else:
                    endorsements['endorsee'] = {
                        'netid': endorsee_netid
                    }
                    endorsements['name'] = ""

            endorsed['endorsed'][endorsee_netid] = endorsements

            messages = get_persistent_messages()
            messages.update(get_persistent_messages(
                tags=list(active_services)))
            endorsed['messages'] = messages

        return self.json_response(endorsed)

    def _endorse(self, to_endorse, service, endorser, endorser_json,
                 endorsee, acted_as, endorsements):
        try:
            e = None
            if to_endorse[service.service_name]['state']:
                reason = to_endorse[service.service_name]['reason']
                if to_endorse.get('store', False):
                    e = service.store_endorsement(
                        endorser, endorsee, acted_as, reason)
                else:
                    e = service.initiate_endorsement(
                        endorser, endorsee, reason)

                endorsements[service.service_name] = e.json_data()
                endorsements[service.service_name]['endorsed'] = True
                endorsements[service.service_name]['reason'] = reason
            else:
                try:
                    e = service.clear_endorsement(
                        endorser, endorsee)

                    if (not endorsee.is_person
                            and not service.supports_shared_netids):
                        # legacy shared netid revoked
                        endorsements[service.service_name] = {
                            'endorser': endorser_json,
                            'endorsee': endorsee.json_data(),
                            'endorsed': False,
                            'is_legacy': True
                        }
                    else:
                        endorsements[service.service_name] = e.json_data()

                except NoEndorsementException as ex:
                    endorsements[service.service_name] = {
                        'endorser': endorser_json,
                        'endorsee': endorsee.json_data(),
                        'endorsed': False
                    }

            if e:
                endorsers = []
                for ee in get_endorsements_for_endorsee(
                        endorsee, category_code=e.category_code):
                    endorsers.append(ee.endorser.json_data())

                endorsements[service.service_name]['endorsers'] = endorsers
        except KeyError as ex:
            if ex.args[0] == 'reason':
                raise MissingReasonException()
        except (CategoryFailureException,
                SubscriptionFailureException) as ex:
            endorsements[service.service_name] = {
                'endorser': endorser_json,
                'endorsee': endorsee.json_data(),
                'category_name': service.category_name,
                'error': "{0}".format(ex)
            }
