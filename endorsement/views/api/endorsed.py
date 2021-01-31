import logging
from userservice.user import UserService
from endorsement.services import (endorsement_services,
                                  endorsement_services_context)
from endorsement.exceptions import UnrecognizedUWNetid
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.user import get_endorser_model, get_endorsee_email_model
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
            if not er.endorsee.is_person:
                continue

            service_tag = None
            for s in endorsement_services():
                if (er.category_code == s.category_code):
                    service_tag = s.service_name
                    break

            if service_tag is None:
                continue

            try:
                if er.endorsee.netid not in endorsed:
                    endorsed[er.endorsee.netid] = {
                        'name': er.endorsee.display_name,
                        'email': get_endorsee_email_model(
                            er.endorsee, endorser).email,
                        'endorsements': endorsement_services_context()
                    }
            except UnrecognizedUWNetid as err:
                logger.error('UnrecognizedUWNetid: {}'.format(err))
                continue

            endorsed[er.endorsee.netid]['endorsements'][
                service_tag] = er.json_data()

            endorsers = []
            for ee in get_endorsements_for_endorsee(
                    er.endorsee, category_code=er.category_code):
                endorsers.append(ee.endorser.json_data())

            endorsed[er.endorsee.netid]['endorsements'][
                service_tag]['endorsers'] = endorsers

        log_resp_time(logger, "endorsed", timer)
        return self.json_response({
            'endorser': endorser.json_data(),
            'endorsed': endorsed
        })
