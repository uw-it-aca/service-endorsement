# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from userservice.user import UserService
from endorsement.models import SharedDriveRecord, ITBillSubscription
from endorsement.util.itbill.shared_drive import (
    subscription_name,
    product_sys_id,
)
from endorsement.exceptions import ITBillSubscriptionNotFound
from restclients_core.exceptions import DataFailureException
from uw_itbill.subscription import Subscription
import json
import logging


logger = logging.getLogger(__name__)


def initiate_subscription(shared_drive_record):
    if shared_drive_record.subscription:
        return

    try:
        user_service = UserService()
        itbill_subscription = ITBillSubscription(
            key_remote=shared_drive_record.get_itbill_key_remote()
        )
        membership = shared_drive_record.shared_drive.members.all()

        data = {
            "name": subscription_name(shared_drive_record),
            "key_remote": itbill_subscription.key_remote,
            "product": product_sys_id(),
            "start_date": "",
            "contact": user_service.get_user(),
            "contacts_additional": ",".join(
                [member.member.netid for member in membership]
            ),
            "lifecycle_state": ITBillSubscription.SUBSCRIPTION_STATE_CHOICES[
                ITBillSubscription.SUBSCRIPTION_DRAFT
            ][1],
            "work_notes": "Subscription initiated by Provision Request Tool",
        }

        Subscription().create_subscription(json.dumps(data))
        itbill_subscription.save()
        shared_drive_record.subscription = itbill_subscription
        shared_drive_record.save()
    except Exception as ex:
        raise ex

    return None


def update_itbill_subscription(member_netid, drive_id):
    record = SharedDriveRecord.objects.get_member_drives(
        member_netid, drive_id
    ).get()

    load_itbill_subscription(record)


def get_subscription_by_key_remote(key_remote):
    try:
        return Subscription().get_subscription_by_key_remote(key_remote)
    except DataFailureException as ex:
        if ex.status == 404:
            raise ITBillSubscriptionNotFound(key_remote)

        raise


def load_itbill_subscription(record):
    """
    Update the subscription record with the latest ITBill data
    """
    record.update_subscription(
        get_subscription_by_key_remote(record.subscription.key_remote)
    )
