# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from endorsement.models import EndorsementRecord
from userservice.user import UserService
from endorsement.services import endorsement_services, is_valid_endorser
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import get_endorsements_for_endorsee
from endorsement.dao.persistent_messages import get_persistent_messages
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
        active_services = set()

        netid_supported = get_supported_resources_for_netid(netid)
        if netid_supported is None:
            netid_supported = []

        for supported in netid_supported:
            endorsements = self._load_shared_endorsements(
                supported, endorser, active_services)

            if endorsements:
                owned.append(endorsements)

        messages = get_persistent_messages()
        messages.update(get_persistent_messages(tags=list(active_services)))

        return self.json_response({
            'endorser': endorser.json_data(),
            'shared': owned,
            'messages': messages
        })

    def _load_shared_endorsements(self, supported, endorser, active_services):
        endorsements = None

        # list and record eligible services and their endorsements
        for service in endorsement_services():
            if not service.valid_supported_netid(supported, endorser):
                continue

            if endorsements is None:
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
                    return None

                endorsements = {
                    'netid': endorsee.netid,
                    'name': endorsee.display_name,
                    'type': supported.netid_type,
                    'endorsements': {}
                }

            try:
                endorsement_record = service.get_endorsement(
                    endorser, endorsee)
                endorsement = endorsement_record.json_data()
                endorsement['endorser'] = endorser.json_data()
                endorsement['endorsers'] = [
                    ee.endorser.json_data()
                    for ee in get_endorsements_for_endorsee(endorsee)
                    if ee.category_code == service.category_code]

                active_services.add(service.service_name)

            except (EndorsementRecord.DoesNotExist,
                    NoEndorsementException):
                endorsement = {
                    'category_name': service.category_name,
                    'valid_shared': True
                }

            endorsements['endorsements'][service.service_name] = endorsement

        return endorsements
