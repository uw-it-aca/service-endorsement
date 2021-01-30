import logging
from userservice.user import UserService
from endorsement.services import endorsement_services
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.uwnetid_supported import (
    get_shared_netids_for_netid, valid_supported_resource)
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
                    'endorsements': {}
                }

                for s in endorsement_services():
                    if valid_supported_resource(shared, s):
                        data['endorsements'][s.service_name] = {
                            'category_name': s.category_name,
                            'valid_shared': True
                        }

                try:
                    endorsee = get_endorsee_model(shared.name)
                    if not endorsee.kerberos_active_permitted:
                        continue

                    data['name'] = endorsee.display_name
                    for endorsement in endorsements:
                        if endorsement.endorsee.id == endorsee.id:
                            _add_endorsements(shared, endorser, endorsee, data)

                except (UnrecognizedUWNetid, InvalidNetID):
                    pass

                owned.append(data)

        log_resp_time(logger, "shared", timer)
        return self.json_response({
            'endorser': endorser.json_data(),
            'shared': owned
        })


def _add_endorsements(shared, endorser, endorsee, data):
    for er in get_endorsements_for_endorsee(endorsee):
        for s in endorsement_services():
            if (er.category_code == s.category_code
                    and valid_supported_resource(shared, s)):
                endorsement = er.json_data()
                endorsement['endorser'] = endorser.json_data()
                endorsement['endorsers'] = [endorser.json_data()]
                data['endorsements'][s.service_name] = endorsement
