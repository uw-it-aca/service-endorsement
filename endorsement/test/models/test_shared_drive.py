# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.core.management import call_command
from datetime import datetime
from endorsement.models import SharedDriveRecord


class TestSharedDrive(TestCase):
    DRIVE_ID = 'ABC_0123-DE45FF5789'
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

    def get_expire_record(self):
        return SharedDriveRecord.objects.get(
            shared_drive__drive_id=self.DRIVE_ID)

    def test_expire_shared_drive(self):
        expire_record = self.get_expire_record()
        self.assertIsNone(expire_record.datetime_deleted)
        original_name = expire_record.shared_drive.drive_name

        expire_record.expire()

        expire_record = self.get_expire_record()
        self.assertIsNotNone(expire_record.datetime_deleted)
        self.assertTrue(expire_record.shared_drive.drive_name != original_name)

    def test_rescue_shared_drive(self):
        expire_record = self.get_expire_record()

        expire_record.expire()

        expire_record = self.get_expire_record()
        expired_name = expire_record.shared_drive.drive_name

        expire_record.rescue_from_deletion()

        expire_record = self.get_expire_record()
        self.assertIsNone(expire_record.datetime_deleted)
        self.assertTrue(expire_record.shared_drive.drive_name != expired_name)
