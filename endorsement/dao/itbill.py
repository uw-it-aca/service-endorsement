# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.conf import settings
from endorsement.models import SharedDrive, SharedDriveRecord
from endorsement.exceptions import (
    SharedDriveRecordExists, ITBillSubscriptionNotFound)
from userservice.user import UserService
from uw_itbill.subscription import Subscription
import logging


logger = logging.getLogger(__name__)


def initiate_subscription(shared_drive_record):
    try:
        user_service = UserService()

        new_subscription = {
            "name": shared_drive_record.subscription.name,
            "key_remote": shared_drive_record.subscription.key_remote,
            "product": getattr(settings, "ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID"),
            "start_date": "",
	    "contact": user_service.get_user(),
	    "contacts_additional": ','.join([
                member.name for member in shared_drive.members.all()]),
	    "lifecycle_state": SharedDriveRecord.STATE_DRAFT,
	    "work_notes": "Subscription initiated by Provision Request Tool",
        }

        return Subscription().create_subscription(new_subscription)
    except SharedDriveRecord.ValidationError as ex:
        raise SharedDriveRecordExists(shared_drive.drive_id)
    except Exception as ex:
        logger.exception("Subscription: for {}: {}".format(subscription, ex))

    return None


def get_subscription_by_key_remote(key_remote):
    try:
        return Subscription().get_subscription_by_key_remote(
            subscription.key_remote)
    except DataFailureException as ex:
        if ex.status == 404:
            raise ITBillSubscriptionNotFound(key_remote)

        raise
