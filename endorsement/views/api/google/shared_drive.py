# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.models import SharedDriveRecord
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.dao.itbill import update_itbill_subscription
from endorsement.dao.shared_drive import (
    sync_quota_from_subscription, shared_drive_lifecycle_expired)
from endorsement.dao.pws import get_person
from endorsement.util.auth import is_support_user
from endorsement.views.rest_dispatch import (
    RESTDispatch, invalid_session, data_not_found,
    invalid_endorser, bad_request, data_error)
from endorsement.exceptions import UnrecognizedUWNetid, InvalidNetID
from restclients_core.exceptions import DataFailureException
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
            netid, acted_as = self._validate_user(
                request, valid_act_as=is_support_user, logger=logger)

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
            netid, acted_as = self._validate_user(request, logger=logger)
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
                if not accept:
                    shared_drive_lifecycle_expired(self)
            else:
                return bad_request(logger)

        except SharedDriveRecord.DoesNotExist:
            return data_not_found(logger)
        except KeyError:
            return bad_request(logger, "Missing accept parameter")

        return self.json_response(self._drive_list(netid, drive_id))

    def _drive_list(self, netid, drive_id=None):
        drives = SharedDriveRecord.objects.get_member_drives(netid, drive_id)
        json_data = [d.json_data() for d in drives]

        # add display_name for member netids
        for drive in json_data:
            for m in drive['drive']['members']:
                try:
                    m['display_name'] = get_person(m['netid']).display_name
                except DataFailureException as ex:
                    m['display_name'] = None

        return {
            'drives': json_data,
            'messages': get_persistent_messages()
        }
