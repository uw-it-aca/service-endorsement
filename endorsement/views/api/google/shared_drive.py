# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from userservice.user import UserService
from endorsement.models import SharedDriveRecord
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, invalid_endorser)
from endorsement.exceptions import UnrecognizedUWNetid, InvalidNetID
import logging


logger = logging.getLogger(__name__)


class SharedDrive(RESTDispatch):
    """
    Return SharedDriveRecords for provided netid
    """
    def get(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        drives = SharedDriveRecord.objects.get_shared_drives_for_netid(netid)

        return self.json_response({
            'drives': [d.json_data() for d in drives],
            'messages': get_persistent_messages()
        })

    def _validate_user(self, request):
        user_service = UserService()
        netid = user_service.get_user()
        if not netid:
            raise UnrecognizedUWNetid()

        original_user = user_service.get_original_user()
        acted_as = None if (netid == original_user) else original_user
        if acted_as and is_only_support_user(request):
            raise InvalidNetID()

        return netid, acted_as
