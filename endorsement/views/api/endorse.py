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
    store_office365_endorsement, clear_office365_endorsement,
    store_google_endorsement, clear_google_endorsement)
from endorsement.dao.notification import notify_endorsees
from endorsement.util.time_helper import Timer
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import InvalidNetID, UnrecognizedUWNetid


logger = logging.getLogger(__name__)


class Endorse(RESTDispatch):
    """
    Validate provided endorsement list
    """
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        timer = Timer()

        endorsees = json.loads(request.read())

        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger, timer)

        endorser = get_endorser_model(netid)
        endorser_pws = get_person(netid)

        endorsed = {
            'endorser': endorser.json_data(),
            'endorser_name': endorser_pws.display_name,
            'endorser_email': endorser_pws.email1,
            'endorsed': {}
        }

        for endorsee_netid, to_endorse in endorsees.iteritems():
            try:
                endorsee = get_endorsee_model(endorsee_netid)
                endorsements = {
                    'name': endorsee.display_name
                }

                if 'email' in to_endorse:
                    endorsements['email'] = get_endorsee_email_model(
                        endorsee, email=to_endorse['email']).email

                if 'o365' in to_endorse:
                    try:
                        if to_endorse['o365']:
                            e = store_office365_endorsement(endorser, endorsee)
                            endorsements['o365'] = e.json_data()
                            endorsements['o365']['endorsed'] = True
                        else:
                            clear_office365_endorsement(endorser, endorsee)
                            endorsements['o365'] = {
                                'endorsed': False
                            }
                    except Exception as ex:
                        raise

                if 'google' in to_endorse:
                    try:
                        if to_endorse['google']:
                            e = store_google_endorsement(endorser, endorsee)
                            endorsements['google'] = e.json_data()
                            endorsements['google']['endorsed'] = True
                        else:
                            clear_google_endorsement(endorser, endorsee)
                            endorsements['google'] = {
                                'endorser': endorser.json_data(),
                                'endorsee': endorsee.json_data(),
                                'endorsed': False
                            }
                    except Exception as ex:
                        raise

            except (KeyError, InvalidNetID, UnrecognizedUWNetid) as ex:
                endorsements = {
                    'endorsee': endorsee.json_data(),
                    'error': '%s' % (ex)
                }

            endorsed['endorsed'][endorsee.netid] = endorsements

        notify_endorsees(endorser, endorsed['endorsed'])

        return self.json_response(endorsed)
