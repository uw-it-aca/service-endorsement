# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import logging
from userservice.user import UserService
from endorsement.services import (get_endorsement_service,
                                  endorsement_services_context)
from endorsement.exceptions import UnrecognizedUWNetid
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.user import get_endorser_model, get_endorsee_email_model
from endorsement.dao.endorse import (
    get_endorsements_by_endorser, get_endorsements_for_endorsee)
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)


logger = logging.getLogger(__name__)


class Endorsed(RESTDispatch):
    """
    Validate provided endorsement list
    """
    def get(self, request, *args, **kwargs):
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger)

        endorser = get_endorser_model(netid)
        endorsed = {}
        for er in get_endorsements_by_endorser(endorser):
            if not er.endorsee.is_person:
                continue

            service = get_endorsement_service(er.category_code)
            if service is None:
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
                service.service_name] = er.json_data()

            endorsers = []
            for ee in get_endorsements_for_endorsee(
                    er.endorsee, category_code=er.category_code):
                endorsers.append(ee.endorser.json_data())

            endorsed[er.endorsee.netid]['endorsements'][
                service.service_name]['endorsers'] = endorsers

        return self.json_response({
            'endorser': endorser.json_data(),
            'endorsed': endorsed
        })
