# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from datetime import datetime
from endorsement.models import SharedDriveRecord, ITBillSubscription


class TestITBill(TestCase):
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

    def test_current_quota(self):
        record = SharedDriveRecord.objects.get(
            shared_drive__drive_id='IRDXB54TWF3OY8MVC9J')

        now = datetime.strptime('2023-12-31', '%Y-%m-%d').date()
        quota = record.subscription.get_quota_on_date(now)
        self.assertEqual(quota, None)

        now = datetime.strptime('2024-01-01', '%Y-%m-%d').date()
        quota = record.subscription.get_quota_on_date(now)
        self.assertEqual(quota, 300)

        now = datetime.strptime('2024-01-02', '%Y-%m-%d').date()
        quota = record.subscription.get_quota_on_date(now)
        self.assertEqual(quota, 300)

        now = datetime.strptime('2024-12-28', '%Y-%m-%d').date()
        quota = record.subscription.get_quota_on_date(now)
        self.assertEqual(quota, 300)

        now = datetime.strptime('2024-12-29', '%Y-%m-%d').date()
        quota = record.subscription.get_quota_on_date(now)
        self.assertEqual(quota, 300)

        now = datetime.strptime('2024-12-30', '%Y-%m-%d').date()
        quota = record.subscription.get_quota_on_date(now)
        self.assertEqual(quota, None)


