import logging
import json
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model, get_endorsee_email_model)
from endorsement.dao.endorse import (
    is_office365_permitted, is_google_permitted,
    get_endorsements_for_endorsee)
from endorsement.dao.gws import is_valid_endorser
from endorsement.util.time_helper import Timer
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import InvalidNetID, UnrecognizedUWNetid
from restclients_core.exceptions import DataFailureException


logger = logging.getLogger(__name__)


class Validate(RESTDispatch):
    """
    Validate provided endorsement list
    """
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        timer = Timer()

        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger, timer)

        endorser = get_endorser_model(netid)

        netids = json.loads(request.read())
        validated = {
            'endorser': endorser.json_data(),
            'validated': []
        }

        for endorse_netid in netids:
            try:
                endorsee = get_endorsee_model(endorse_netid)
                endorsements = get_endorsements_for_endorsee(endorsee)
                active = False
                valid = {
                    'netid': endorse_netid,
                    'name': endorsee.display_name,
                    'email': get_endorsee_email_model(endorsee).email
                }

                for e in endorsements:
                    if e.reason and len(e.reason):
                        valid['reason'] = e.reason
                        break

                try:
                    active, endorsed = is_office365_permitted(
                        endorser, endorsee)
                    valid['o365'] = {
                        'active': active,
                        'endorsers': [],
                        'self_endorsed': endorsed
                    }

                    for e in endorsements:
                        if (e.category_code ==
                                EndorsementRecord.OFFICE_365_ENDORSEE):
                            valid['o365']['endorsers'].append(e.endorser.netid)

                except Exception as ex:
                    valid['o365'] = {
                        'error': "%s" % ex
                    }

                try:
                    active, endorsed = is_google_permitted(
                        endorser, endorsee)
                    valid['google'] = {
                        'active': active,
                        'endorsers': [],
                        'self_endorsed': endorsed
                    }

                    for e in endorsements:
                        if (e.category_code ==
                                EndorsementRecord.GOOGLE_SUITE_ENDORSEE):
                            valid['google']['endorsers'].append(
                                e.endorser.netid)

                except Exception as ex:
                    valid['google'] = {
                        'error': "%s" % ex
                    }

            except (InvalidNetID, UnrecognizedUWNetid) as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': '%s' % (ex)
                }
            except Exception as ex:
                valid = {
                    'netid': endorse_netid,
                    'error': '%s' % (ex)
                }

            validated['validated'].append(valid)

        return self.json_response(validated)
