# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import logging
from django.conf import settings
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.services import endorsement_services, is_valid_endorser
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model,
    get_endorsee_email_model, is_shared_netid)
from endorsement.dao.endorse import (
    get_endorsements_for_endorsee, get_endorsements_by_endorser)
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import (
    InvalidNetID, UnrecognizedUWNetid, TooManyUWNetids, SharedUWNetid)


logger = logging.getLogger(__name__)


class Validate(RESTDispatch):
    """
    Validate provided endorsement list
    """
    def post(self, request, *args, **kwargs):
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger)

        endorser = get_endorser_model(netid)
        netids = request.data.get('netids', [])
        validated = {
            'endorser': endorser.json_data(),
            'validated': []
        }

        endorsements = get_endorsements_by_endorser(endorser)
        max_netids = getattr(settings, "ENDORSER_LIMIT", 300)
        netid_count = max_netids - endorsements.filter(
            endorsee__is_person=True).count()

        for endorse_netid in netids:
            try:
                endorsee = get_endorsee_model(endorse_netid)
                if not endorsee.is_person:
                    if is_shared_netid(endorsee.netid):
                        raise SharedUWNetid(
                            '{0} is a Shared NetID'.format(endorse_netid))
                    else:
                        raise InvalidNetID(
                            '{0} not a personal NetID'.format(endorse_netid))

                netid_count -= 1
                if netid_count < 0:
                    raise TooManyUWNetids()

                endorsements = get_endorsements_for_endorsee(endorsee)
                valid = {
                    'netid': endorse_netid,
                    'name': endorsee.display_name,
                    'email': get_endorsee_email_model(
                        endorsee, endorser).email,
                    'endorsements': {}
                }

                for e in endorsements:
                    if e.reason and len(e.reason):
                        valid['reason'] = e.reason
                        break

                for s in endorsement_services():
                    if s.valid_person_endorsee(endorsee):
                        valid['endorsements'][
                            s.service_name] = self._endorsement(
                                endorser, endorsee, s.is_permitted,
                                endorsements, s.category_code)

            except UnrecognizedUWNetid as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Unrecognized NetID: {0}'.format(ex),
                }
            except SharedUWNetid as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Shared NetID: {0}'.format(ex),
                    'is_shared': True
                }
            except InvalidNetID as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': '{0}'.format(ex),
                    'is_ineligible': True
                }
            except TooManyUWNetids:
                valid = {
                    'netid': endorse_netid,
                    'error': 'Provision Count Exceeded',
                    'error_message':
                        'Limit of {0} provisioned netids exceeded'.format(
                            max_netids)
                }
            except Exception as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': '{0}'.format(ex)
                }

            validated['validated'].append(valid)

        return self.json_response(validated)

    def _endorsement(self, endorser, endorsee, is_permitted,
                     endorsements, endorsement_category):
        try:
            endorsement = {
                'category_name': self.category_name(endorsement_category),
                'endorsers': []
            }

            active, endorsed = is_permitted(endorser, endorsee)
            endorsement['active'] = active
            endorsement['self_endorsed'] = endorsed

            for e in endorsements:
                if (e.category_code == endorsement_category):
                    endorsement['endorsers'].append(e.endorser.json_data())

        except Exception as ex:
            endorsement['error'] = '{0}'.format(ex)

        return endorsement

    def category_name(self, category_code):
        return dict(EndorsementRecord.CATEGORY_CODE_CHOICES)[category_code]
