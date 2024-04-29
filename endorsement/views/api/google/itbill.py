# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models import SharedDriveRecord
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.dao.itbill import initiate_subscription
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, data_not_found,
    invalid_endorser, bad_request, data_error)
from endorsement.exceptions import UnrecognizedUWNetid, InvalidNetID
import logging


logger = logging.getLogger(__name__)


class SharedDriveITBill(RESTDispatch):
    """
    Manipulate ITBill resource SharedDriveRecords for provided netid
    """
    def get(self, request, *args, **kwargs):
        """
        Return SharedDriveRecord with suitable ITBill resource values
        """
        try:
            netid, acted_as = self._validate_user(request)
        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)

        try:
            drive_id = self.kwargs.get('drive_id')
            drive = SharedDriveRecord.objects.get_shared_drives_for_netid(
                netid, drive_id)[0]

            try:

                subscription = initiate_subscription(drive)
                drive.subscription.url = subscription.url
                drive.save()
            except Exception as ex:
                return data_error(
                    logger, "Error initiating subscription: {}".format(ex))

        except SharedDriveRecord.DoesNotExist:
            return data_not_found(logger)

        return self.json_response(self._drive_list(netid, drive_id))

    def _drive_list(self, netid, drive_id=None):
        drives = SharedDriveRecord.objects.get_shared_drives_for_netid(
            netid, drive_id)

        return {
            'drives': [d.json_data() for d in drives],
            'messages': get_persistent_messages()
        }

