# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging

from restclients_core.exceptions import InvalidNetID

from endorsement.dao.itbill import initiate_subscription
from endorsement.dao.persistent_messages import get_persistent_messages
from endorsement.exceptions import (
    ITBillSubscriptionNotFound,
    UnrecognizedUWNetid,
)
from endorsement.models import ITBillSubscription, SharedDriveRecord
from endorsement.util.auth import is_support_user
from endorsement.views.rest_dispatch import (
    RESTDispatch,
    data_error,
    data_not_found,
    invalid_endorser,
    invalid_session,
)

logger = logging.getLogger(__name__)


class SharedDriveITBillURL(RESTDispatch):
    """
    Retrieve ITBill Form URL settings subsciption state
    """
    def get(self, request, *args, **kwargs):
        """
        Instantiate a subscription for the provided netid
        """
        try:
            netid, _acted_as = self._validate_user(
                request, valid_act_as=is_support_user, logger=logger)
            drive_id = self.kwargs.get('drive_id')
            drive = self._get_drive(netid, drive_id)

            if not drive.subscription:
                initiate_subscription(drive)

            drive.subscription.query_priority = \
                ITBillSubscription.PRIORITY_HIGH
            drive.subscription.save()

            return self.json_response({
                'drives': [self._get_drive(
                    netid, drive_id).json_data()],
                'messages': get_persistent_messages()
            })

        except UnrecognizedUWNetid:
            return invalid_session(logger)
        except InvalidNetID:
            return invalid_endorser(logger)
        except (TypeError, ITBillSubscriptionNotFound):
            return data_not_found(logger)
        except Exception as ex:
            return data_error(logger, ex)

    def _get_drive(self, netid, drive_id):
        drives = SharedDriveRecord.objects.get_member_drives(netid, drive_id)

        return drives.get() if drives.count() == 1 else None
