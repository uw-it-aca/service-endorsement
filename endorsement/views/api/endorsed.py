import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.user import get_endorser_model
from endorsement.dao.endorse import (
    get_endorsements_by_endorser, get_endorsements_for_endorsee)
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

        endorser = get_endorser_model(netid)
        endorsed = {}
        for er in get_endorsements_by_endorser(endorser):
            endorsement_type = 'o365' if (
                er.subscription_code == EndorsementRecord.OFFICE_365) else\
                'o365_test' if (
                    er.subscription_code ==
                    EndorsementRecord.OFFICE_365_TEST) else\
                'google' if (
                    er.subscription_code ==
                    EndorsementRecord.GOOGLE_APPS) else\
                'google_test' if (
                    er.subscription_code ==
                    EndorsementRecord.GOOGLE_APPS_TEST) else'unknown'

            if er.endorsee.netid in endorsed:
                endorsed[er.endorsee.netid][endorsement_type] = er.json_data()
            else:
                endorsed[er.endorsee.netid] = {
                    endorsement_type: er.json_data()
                }

            endorsed[er.endorsee.netid][endorsement_type]['endorsed'] = True

            endorsers = []
            for ee in get_endorsements_for_endorsee(er.endorsee):
                if er.subscription_code == ee.subscription_code:
                    endorsers.append(ee.endorser.json_data())

            endorsed[er.endorsee.netid][endorsement_type]['endorsers'] =\
                endorsers

        log_resp_time(logger, "endorsed", timer)
        return self.json_response({
            'endorser': endorser.json_data(),
            'endorsed': endorsed
        })
