# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from django.test import override_settings
from django.test.utils import override_settings
from uw_itbill.subscription import Subscription
from endorsement.dao.itbill import (
    initiate_subscription, load_itbill_subscription)
from endorsement.models import SharedDriveRecord, ITBillSubscription
from endorsement.test.api import EndorsementApiTest


@override_settings(
    ITBILL_SHARED_DRIVE_PRODUCT_SYS_ID='7078586b2f6cb076cad75ae9aab3ea05')
class TestITBill(EndorsementApiTest):
    fixtures = [
        'test_data/member.json',
        'test_data/role.json',
        'test_data/itbill_subscription.json',
        'test_data/itbill_provision.json',
        'test_data/itbill_quantity.json',
        'test_data/shared_drive_member.json',
        'test_data/shared_drive_quota.json',
        'test_data/shared_drive.json',
        'test_data/shared_drive_record.json'
    ]

    def test_itbill_data_load(self):
        key_remote = 'GSD_test_test_test_123_rk'
        drive_id = '9F97529B38CF46F336C7408'

        record = SharedDriveRecord.objects.get_record_by_drive_id(drive_id)

        json_data = record.json_data()
        self.assertEqual(json_data['subscription']['key_remote'], key_remote)
        self.assertEqual(
            len(json_data['subscription']['provisions']), 1)
        self.assertEqual(
            len(json_data['subscription']['provisions'][0]['quantities']), 1)

        load_itbill_subscription(record)

        record = SharedDriveRecord.objects.get_record_by_drive_id(drive_id)
        json_data = record.json_data()
        self.assertEqual(json_data['subscription']['key_remote'], key_remote)
        self.assertEqual(
            len(json_data['subscription']['provisions']), 1)
        self.assertEqual(
            len(json_data['subscription']['provisions'][0]['quantities']), 2)
