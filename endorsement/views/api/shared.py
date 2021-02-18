import logging
from userservice.user import UserService
from endorsement.services import endorsement_services
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
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
        for supported in get_supported_resources_for_netid(netid):
            data = {
                'netid': supported.name,
                'name': None,
                'type': supported.netid_type
            }

            netid_endorsements = {}
            for service in endorsement_services():
                if service.valid_supported_netid(supported):
                    netid_endorsements[service.service_name] = {
                        'category_name': service.category_name,
                        'valid_shared': True
                    }

                    try:
                        endorsee = get_endorsee_model(supported.name)
                        if not endorsee.kerberos_active_permitted:
                            continue

                        data['name'] = endorsee.display_name
                        for endorsement in endorsements:
                            if endorsement.endorsee.id == endorsee.id:
                                _add_endorsements(
                                    supported, endorser, endorsee, data)

                    except (UnrecognizedUWNetid, InvalidNetID):
                        pass

            if netid_endorsements:
                data['endorsements'] = netid_endorsements
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
                    and s.valid_shared_netid(shared)):
                endorsement = er.json_data()
                endorsement['endorser'] = endorser.json_data()
                endorsement['endorsers'] = [endorser.json_data()]
                data['endorsements'][s.service_name] = endorsement
