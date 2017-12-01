import logging
import json
import traceback
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.dao.user import get_endorser_model
from endorsement.dao.gws import is_valid_endorser
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time
from endorsement.views.session import log_session_key
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session)


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

        # fake validating netids for endorsement
        netids = json.loads(request.read())

        # fake setting the endorsements
        from random import uniform

        validated = []
        for netid in netids:

            valid_netid = uniform(0, 1) > 0.15
            eligible_netid = valid_netid and uniform(0, 1) > 0.1

            o365_active = eligible_netid and (uniform(0, 1) > 0.25)
            o365_endorsers = None
            o365_by_you = False
            if (o365_active and uniform(0, 1) > 0.3):
                o365_by_you = o365_active and uniform(0, 1) < 0.5
                o365_endorsers = ['you' if o365_by_you else 'mumble']
                if uniform(0, 1) < 0.5:
                    o365_endorsers.append('garble')
                if uniform(0, 1) < 0.5:
                    o365_endorsers.append('marble')

            google_active = eligible_netid and (uniform(0, 1) > 0.25)
            google_endorsers = None
            google_by_you = False
            if (google_active and uniform(0, 1) > 0.3):
                google_by_you = google_active and uniform(0, 1) < 0.5
                google_endorsers = ['you' if google_by_you else 'mumble']
                if uniform(0, 1) < 0.5:
                    google_endorsers.append('garble')
                if uniform(0, 1) < 0.5:
                    google_endorsers.append('marble')

            validated.append({
                'netid': netid,
                'valid_netid': valid_netid,
                'name': netid + '. Lastname',
                'email': netid + '@uw.edu',
                'subscription': {
                    'google': {
                        'eligible': eligible_netid,
                        'active': google_active,
                        'endorsers': google_endorsers,
                        'self_endorsed': google_by_you,
                        'error': None
                    },
                    'o365': {
                        'eligible': eligible_netid,
                        'active': o365_active,
                        'endorsers': o365_endorsers,
                        'self_endorsed': o365_by_you,
                        'error': None
                    }
                }
            })

        return self.json_response(validated)
