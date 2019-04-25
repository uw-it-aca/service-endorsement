import logging
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from userservice.user import UserService
from endorsement.models import EndorsementRecord
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.uwnetid_supported import get_shared_netids_for_netid
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import (
    get_endorsements_by_endorser, get_endorsements_for_endorsee)
from endorsement.util.time_helper import Timer
from endorsement.util.log import log_resp_time
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import UnrecognizedUWNetid, InvalidNetID


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
        endorsements = get_endorsements_by_endorser(endorser)
        owned = []
        for shared in get_shared_netids_for_netid(netid):
            if shared.is_owner():
                data = {
                    'netid': shared.name,
                    'name': None,
                    'role': shared.role,
                    'endorsements': {
                        'o365': {
                            'category_name': dict(
                                EndorsementRecord.CATEGORY_CODE_CHOICES)[
                                    EndorsementRecord.OFFICE_365_ENDORSEE]
                        },
                        'google': {
                            'category_name': dict(
                                EndorsementRecord.CATEGORY_CODE_CHOICES)[
                                    EndorsementRecord.GOOGLE_SUITE_ENDORSEE]
                        }
                    }
                }

                try:
                    endorsee = get_endorsee_model(shared.name)
                    if not endorsee.kerberos_active_permitted:
                        continue

                    data['name'] = endorsee.display_name
                    for endorsement in endorsements:
                        if endorsement.endorsee.id == endorsee.id:
                            for er in get_endorsements_for_endorsee(endorsee):
                                if (EndorsementRecord.OFFICE_365_ENDORSEE ==
                                        er.category_code):
                                    e_data = er.json_data()
                                    e_data['endorser'] = endorser.json_data()
                                    e_data['endorsers'] = [
                                        endorser.json_data()
                                    ]
                                    data['endorsements']['o365'] = e_data

                                if (EndorsementRecord.GOOGLE_SUITE_ENDORSEE ==
                                        er.category_code):
                                    e_data = er.json_data()
                                    e_data['endorser'] = endorser.json_data()
                                    e_data['endorsers'] = [
                                        endorser.json_data()
                                    ]
                                    data['endorsements']['google'] = e_data

                except (UnrecognizedUWNetid, InvalidNetID):
                    pass

                owned.append(data)

        log_resp_time(logger, "shared", timer)
        return self.json_response({
            'endorser': endorser.json_data(),
            'shared': owned
        })
