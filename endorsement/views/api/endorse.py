import logging
from userservice.user import UserService
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model, get_endorsee_email_model)
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.pws import get_person
from endorsement.dao.endorse import (
    initiate_office365_endorsement, store_office365_endorsement,
    clear_office365_endorsement,
    initiate_google_endorsement, store_google_endorsement,
    clear_google_endorsement,
    initiate_canvas_endorsement, store_canvas_endorsement,
    clear_canvas_endorsement,
    get_endorsements_for_endorsee)
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
    _store_endorsement = {
        'o365': store_office365_endorsement,
        'google': store_google_endorsement,
        'canvas': store_canvas_endorsement
    }

    _initiate_endorsement = {
        'o365': initiate_office365_endorsement,
        'google': initiate_google_endorsement,
        'canvas': initiate_canvas_endorsement
    }

    _clear_endorsement = {
        'o365': clear_office365_endorsement,
        'google': clear_google_endorsement,
        'canvas': clear_canvas_endorsement
    }

    def post(self, request, *args, **kwargs):
        timer = Timer()

        endorsees = request.data.get('endorsees', {})
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
                    'is_person': endorsee.is_person,
                    'endorsements': {}
                }

                if 'email' in to_endorse:
                    endorsements['email'] = get_endorsee_email_model(
                        endorsee, endorser, email=to_endorse['email']).email

                self._endorse(to_endorse, 'o365', endorser, endorser_json,
                              endorsee, acted_as, endorsements['endorsements'])

                self._endorse(to_endorse, 'google', endorser, endorser_json,
                              endorsee, acted_as, endorsements['endorsements'])

                self._endorse(to_endorse, 'canvas', endorser, endorser_json,
                              endorsee, acted_as, endorsements['endorsements'])

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

    def _endorse(self, to_endorse, service_tag, endorser, endorser_json,
                 endorsee, acted_as, endorsements):
        try:
            e = None
            if to_endorse[service_tag]['state']:
                reason = to_endorse[service_tag]['reason']
                if to_endorse.get('store', False):
                    e = self._store_endorsement[service_tag](
                        endorser, endorsee, acted_as, reason)
                else:
                    e = self._initiate_endorsement[service_tag](
                        endorser, endorsee, reason)

                endorsements[service_tag] = e.json_data()
                endorsements[service_tag]['endorsed'] = True
                endorsements[service_tag]['reason'] = reason
            else:
                try:
                    e = self._clear_endorsement[service_tag](
                        endorser, endorsee)
                    endorsements[service_tag] = e.json_data()
                except NoEndorsementException as ex:
                    endorsements[service_tag] = {
                        'endorser': endorser_json,
                        'endorsee': endorsee.json_data(),
                        'endorsed': False
                    }

            if e:
                endorsers = []
                for ee in get_endorsements_for_endorsee(
                        endorsee, category_code=e.category_code):
                    endorsers.append(ee.endorser.json_data())

                endorsements[service_tag]['endorsers'] = endorsers
        except KeyError as ex:
            if ex.args[0] == 'reason':
                raise MissingReasonException()
        except (CategoryFailureException,
                SubscriptionFailureException) as ex:
            endorsements[service_tag] = {
                'endorser': endorser_json,
                'endorsee': endorsee.json_data(),
                'error': "{0}".format(ex)
            }
