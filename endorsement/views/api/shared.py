# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import logging
from endorsement.models import EndorsementRecord
from userservice.user import UserService
from endorsement.services import endorsement_services
from endorsement.dao.gws import is_valid_endorser
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import get_endorsements_for_endorsee
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import (
    NoEndorsementException, UnrecognizedUWNetid, InvalidNetID)


logger = logging.getLogger(__name__)


class Shared(RESTDispatch):
    """
    Return shared netids associated with the provided netid
    """
    def get(self, request, *args, **kwargs):
        netid = UserService().get_user()
        if not netid:
            return invalid_session(logger)

        if not is_valid_endorser(netid):
            return invalid_endorser(logger)

        endorser = get_endorser_model(netid)
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
                if not service.valid_supported_netid(supported, endorser):
                    continue

                try:
                    endorsement = service.get_endorsement(
                        endorser, endorsee).json_data()
                    endorsement['endorser'] = endorser.json_data()
                    endorsement['endorsers'] = [
                        ee.endorser.json_data()
                        for ee in get_endorsements_for_endorsee(endorsee)
                        if ee.category_code == service.category_code]
                except (EndorsementRecord.DoesNotExist,
                        NoEndorsementException):
                    endorsement = {
                        'category_name': service.category_name,
                        'valid_shared': True
                    }

                data['endorsements'][service.service_name] = endorsement

            if data['endorsements']:
                owned.append(data)

        return self.json_response({
            'endorser': endorser.json_data(),
            'shared': owned
        })
