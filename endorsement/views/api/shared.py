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
            # make sure endorsee is base-line valid (i.e.,
            # has pws entry, kerberos principle and such)
            try:
                endorsee = get_endorsee_model(supported.name)
                if not endorsee.kerberos_active_permitted:
                    logger.info(("Skip shared netid {}: "
                                 "inactive kerberos permit").format(
                                     supported.name))
                    continue
            except (UnrecognizedUWNetid, InvalidNetID):
                logger.info(("Skip shared netid {}: "
                             "Unrecognized or invalid netid").format(
                                 supported.name))
                continue

            data = {
                'netid': endorsee.netid,
                'name': endorsee.display_name,
                'type': supported.netid_type,
                'endorsements': {}
            }

            # list and record eligible services and their endorsements
            for service in endorsement_services():
                if not service.valid_supported_netid(supported):
                    continue

                # indicate eligibility
                endorsement = {
                    'category_name': service.category_name,
                    'valid_shared': True
                }

                # with current endorsement if present
                for er in endorsements:
                    if er.category_code == service.category_code:
                        endorsement = er.json_data()
                        endorsement['endorser'] = er.endorser.json_data()

                # record other endorsers
                endorsement['endorsers'] = []
                for er in get_endorsements_for_endorsee(endorsee):
                    if er.category_code == service.category_code:
                        endorsement['endorsers'].append(
                            er.endorser.json_data())

                data['endorsements'][service.service_name] = endorsement

            if data['endorsements']:
                owned.append(data)

        log_resp_time(logger, "shared", timer)
        return self.json_response({
            'endorser': endorser.json_data(),
            'shared': owned
        })
