import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.dao.gws import is_valid_endorser
from endorsement.models import Endorser, EndorsementRecord
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)


logger = logging.getLogger(__name__)


class Endorsed(RESTDispatch):
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

        endorsed = []
        try:
            endorser = Endorser.objects.get(netid=netid)
            for er in EndorsementRecord.objects.get(endorser=endorser):
                endorsee = er.json_data()
                endorsee['endorsers'] = []
                for ee in EndorsementRecord.objects.get(endorsee=er.netid):
                    endorsee['endorsers'].append(ee.json_data())
        except (Endorser.DoesNotExist, EndorsementRecord.DoesNotExist):
            pass

        log_resp_time(logger, "endorsed", timer)
        return self.json_response(endorsed)
