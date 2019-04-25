import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.user import get_endorser_model
from endorsement.dao.endorse import (
    get_endorsements_by_endorser, get_endorsements_for_endorsee)
from endorsement.dao.uwnetid_supported import get_shared_netids_for_netid
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
        category_choices = dict(EndorsementRecord.CATEGORY_CODE_CHOICES)
        for er in get_endorsements_by_endorser(endorser):
            if not er.endorsee.is_person:
                continue

            endorsement_type = 'unknown'
            if (er.category_code == EndorsementRecord.OFFICE_365_ENDORSEE):
                endorsement_type = 'o365'
            elif er.category_code == EndorsementRecord.GOOGLE_SUITE_ENDORSEE:
                endorsement_type = 'google'
            else:
                continue

            if er.endorsee.netid not in endorsed:
                endorsed[er.endorsee.netid] = {
                    'name': er.endorsee.display_name,
                    'endorsements': {
                        'o365': {
                            'category_name': category_choices[
                                    EndorsementRecord.OFFICE_365_ENDORSEE]
                        },
                        'google': {
                            'category_name': category_choices[
                                    EndorsementRecord.GOOGLE_SUITE_ENDORSEE]
                        }
                    }
                }

            endorsed[er.endorsee.netid]['endorsements'][
                endorsement_type] = er.json_data()

            endorsed[er.endorsee.netid]['endorsements'][
                endorsement_type]['endorsed'] = True

            endorsers = []
            for ee in get_endorsements_for_endorsee(er.endorsee):
                if er.category_code == ee.category_code:
                    endorsers.append(ee.endorser.json_data())

            endorsed[er.endorsee.netid]['endorsements'][
                endorsement_type]['endorsers'] = endorsers

        log_resp_time(logger, "endorsed", timer)
        return self.json_response({
            'endorser': endorser.json_data(),
            'endorsed': endorsed
        })
