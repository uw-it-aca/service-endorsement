# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models import SharedDriveRecord
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.dao.itbill import update_itbill_subscription
from endorsement.dao.shared_drive import sync_quota_from_subscription
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, data_not_found,
    invalid_endorser, bad_request, data_error)
from endorsement.exceptions import UnrecognizedUWNetid, InvalidNetID
import logging


logger = logging.getLogger(__name__)


class SharedDrive(RESTDispatch):
    """
    Manipulate SharedDriveRecords for provided netid
    """
    def get(self, request, *args, **kwargs):
        """
        Return SharedDriveRecords for provided netid, all or by drive_id
        """
        try:
            netid, acted_as = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        drive_id = self.kwargs.get('drive_id')
        refresh = request.GET.get('refresh')

        try:
            if drive_id and refresh:
                update_itbill_subscription(netid, drive_id)
                sync_quota_from_subscription(drive_id)
        except Exception as ex:
            logger.exception("refresh_subscription: {}".format(ex))
            return data_error(logger, ex)

        return self.json_response(self._drive_list(netid, drive_id))

    def put(self, request, *args, **kwargs):
        try:
            netid, acted_as = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        try:
            drive_id = self.kwargs['drive_id']
            drive = SharedDriveRecord.objects.get_member_drives(
                netid, drive_id).get()

            accept = request.data.get('accept')
            if isinstance(accept, bool):
                drive.set_acceptance(netid, accept, acted_as)
            else:
                return bad_request(logger)

        except SharedDriveRecord.DoesNotExist:
            return data_not_found(logger)
        except KeyError:
            return bad_request(logger, "Missing accept parameter")

        return self.json_response(self._drive_list(netid, drive_id))

    def _drive_list(self, netid, drive_id=None):
        drives = SharedDriveRecord.objects.get_member_drives(netid, drive_id)

        return {
            'drives': [d.json_data() for d in drives],
            'messages': get_persistent_messages()
        }
