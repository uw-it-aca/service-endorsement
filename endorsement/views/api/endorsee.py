import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.user import get_endorsee_model
from endorsement.dao.endorse import get_endorsements_for_endorsee
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)


logger = logging.getLogger(__name__)


class Endorsee(RESTDispatch):
    """
    Validate provided endorsement list
    """
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        timer = Timer()

        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger, timer)

        endorsee_netid = self.kwargs['endorsee']
        endorsee = get_endorsee_model(endorsee_netid)
        endorsees = {
            'endorsee': endorsee.netid,
            'endorsements': []
        }

        for er in get_endorsements_for_endorsee(endorsee):
            endorsees['endorsements'].append(er.json_data())

        log_resp_time(logger, "endorsee", timer)
        return self.json_response(endorsees)
