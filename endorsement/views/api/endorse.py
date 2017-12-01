import logging
import traceback
import json
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

        # fake setting the endorsements
        from random import uniform

        import pdb; pdb.set_trace()

        endorsed = []
        for endorsee, to_endorse in endorsees.iteritems():
            endorse_result = {
                'netid': endorsee,
                'endorsement': {}
            }

            if 'o365' in to_endorse:
                if uniform(0, 1) < 0.1:
                    endorse_result['endorsement']['o365'] = {
                        'error': 'server is down'
                    }
                elif to_endorse['o365']:
                    endorse_result['endorsement']['o365'] = {
                        'endorsed': True
                    }
                else:
                    endorse_result['endorsement']['o365'] = {
                        'endorsed': False
                    }

            if 'google' in to_endorse:
                if uniform(0, 1) < 0.1:
                    endorse_result['endorsement']['google'] = {
                        'error': 'server is down'
                    }
                elif to_endorse['google']:
                    endorse_result['endorsement']['google'] = {
                        'endorsed': True
                    }
                else:
                    endorse_result['endorsement']['google'] = {
                        'endorsed': False
                    }

            endorsed.append(endorse_result)

        return self.json_response(endorsed)
