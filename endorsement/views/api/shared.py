import logging
from userservice.user import UserService
from endorsement.services import ENDORSEMENT_SERVICES, endorsement_service_keys
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
                    'type': shared.netid_type,
                    'endorsements': endorsement_service_keys(
                        ['category_name', 'valid_shared'], shared=True)
                }

                try:
                    endorsee = get_endorsee_model(shared.name)
                    if not endorsee.kerberos_active_permitted:
                        continue

                    data['name'] = endorsee.display_name
                    for endorsement in endorsements:
                        if endorsement.endorsee.id == endorsee.id:
                            for er in get_endorsements_for_endorsee(endorsee):
                                for svc_tag, v in ENDORSEMENT_SERVICES.items():
                                    if (er.category_code == v['category_code'] and
                                            v['valid_shared']):
                                        data['endorsements'][svc_tag]\
                                            = er.json_data()
                                        data['endorsements'][svc_tag][
                                            'endorser'] = endorser.json_data()
                                        data['endorsements'][svc_tag][
                                            'endorsers'] = [
                                                endorser.json_data()]

                except (UnrecognizedUWNetid, InvalidNetID):
                    pass

                owned.append(data)

        log_resp_time(logger, "shared", timer)
        return self.json_response({
            'endorser': endorser.json_data(),
            'shared': owned
        })
