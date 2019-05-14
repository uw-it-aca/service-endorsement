import logging
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model, get_endorsee_email_model)
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.pws import get_person
from endorsement.dao.endorse import (
    initiate_office365_endorsement, store_office365_endorsement,
    clear_office365_endorsement,
    initiate_google_endorsement, store_google_endorsement,
    clear_google_endorsement)
from endorsement.util.time_helper import Timer
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import (
    InvalidNetID, UnrecognizedUWNetid, NoEndorsementException,
    CategoryFailureException, SubscriptionFailureException,
    MissingReasonException)


logger = logging.getLogger(__name__)


class Endorse(RESTDispatch):
    """
    Validate provided endorsement list
    """
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        timer = Timer()

        endorsees = json.loads(request.read())

        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            return invalid_session(logger, timer)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger, timer)

        original_user = user_service.get_original_user()
        acted_as = None if (netid == original_user) else original_user

        endorser = get_endorser_model(netid)
        endorser_json = endorser.json_data()
        endorser_pws = get_person(netid)

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
                    'endorsements': {}
                }

                if 'email' in to_endorse:
                    endorsements['email'] = get_endorsee_email_model(
                        endorsee, endorser, email=to_endorse['email']).email

                try:
                    if to_endorse['o365']['state']:
                        reason = to_endorse['o365']['reason']
                        e = None
                        if to_endorse.get('store', False):
                            e = store_office365_endorsement(
                                endorser, endorsee, acted_as, reason)
                        else:
                            e = initiate_office365_endorsement(
                                endorser, endorsee, reason)

                        endorsements['endorsements']['o365'] = e.json_data()
                        endorsements['endorsements']['o365']['endorsed'] = True
                        endorsements['endorsements']['o365']['reason'] = reason
                    else:
                        try:
                            clear_office365_endorsement(endorser, endorsee)
                        except NoEndorsementException as ex:
                            pass

                        endorsements['endorsements']['o365'] = {
                            'endorsed': False
                        }
                except KeyError as ex:
                    if ex.args[0] == 'reason':
                        raise MissingReasonException()
                except (CategoryFailureException,
                        SubscriptionFailureException) as ex:
                    endorsements['endorsements']['o365'] = {
                        'endorser': endorser_json,
                        'endorsee': endorsee.json_data(),
                        'error': "{0}".format(ex)
                    }

                try:
                    if to_endorse['google']['state']:
                        reason = to_endorse['google']['reason']
                        e = None
                        if to_endorse.get('store', False):
                            e = store_google_endorsement(
                                endorser, endorsee, acted_as, reason)
                        else:
                            e = initiate_google_endorsement(
                                endorser, endorsee, reason)

                        endorsements['endorsements'][
                            'google'] = e.json_data()
                        endorsements['endorsements'][
                            'google']['endorsed'] = True
                        endorsements['endorsements'][
                            'google']['reason'] = reason
                    else:
                        try:
                            clear_google_endorsement(endorser, endorsee)
                        except NoEndorsementException as ex:
                            pass

                        endorsements['endorsements']['google'] = {
                            'endorser': endorser_json,
                            'endorsee': endorsee.json_data(),
                            'endorsed': False
                        }
                except KeyError as ex:
                    if ex.args[0] == 'reason':
                        raise MissingReasonException()
                except (CategoryFailureException,
                        SubscriptionFailureException) as ex:
                    endorsements['endorsements']['google'] = {
                        'endorser': endorser_json,
                        'endorsee': endorsee.json_data(),
                        'error': "{0}".format(ex)
                    }

            except InvalidNetID as ex:
                endorsements = {
                    'endorsee': {
                        'netid': endorsee_netid
                    },
                    'name': "",
                    'error': '{0}'.format(ex)
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

        return self.json_response(endorsed)
