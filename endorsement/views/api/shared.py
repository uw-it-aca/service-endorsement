import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.uwnetid_supported import get_shared_netids_for_netid
from endorsement.dao.user import get_endorser_model
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)


logger = logging.getLogger(__name__)


class Shared(RESTDispatch):
    """
    Return shared netids associated with the provided netid
    """
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        timer = Timer()

        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger, timer)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger, timer)

        endorser = get_endorser_model(netid)
        owned = []
        for shared in get_shared_netids_for_netid(netid):
            if shared.is_owner():
                owned.append(shared.json_data())

        log_resp_time(logger, "shared", timer)
        return self.json_response({
            'endorser': endorser.json_data(),
            'shared': owned
        })
