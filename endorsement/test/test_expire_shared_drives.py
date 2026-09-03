# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from endorsement.models import SharedDriveRecord


class TestExpireSharedDrives(TestCase):
    DRIVE_ID = 'ABC_0123-DE45FF5789'

    def setUp(self):
        _output = call_command('initialize_db')
        expire_record = self.get_expire_record()
        self.DRIVE_NAME = expire_record.shared_drive.drive_name
        expire_record.datetime_notice_1_emailed = "2024-01-01T00:00:00Z"
        expire_record.datetime_notice_2_emailed = "2024-03-01T00:00:00Z"
        expire_record.datetime_notice_3_emailed = "2024-03-30T00:00:00Z"
        expire_record.datetime_notice_4_emailed = "2024-04-07T00:00:00Z"
        expire_record.save()

    def get_expire_record(self):
        return SharedDriveRecord.objects.get(
            shared_drive__drive_id=self.DRIVE_ID)

    def call_command(self, *args, **kwargs):
        out = StringIO()
        _output = call_command('expire_shared_drives',
                               *args, stdout=out, stderr=StringIO(), **kwargs)
        return out.getvalue()

    @patch('endorsement.management.commands.expire_shared_drives.logger')
    def test_expire_shared_drives_logging(self, mock_logger):
        _output = self.call_command()
        mock_logger.info.assert_called_with(
            f'Expiring: {self.DRIVE_ID} "{self.DRIVE_NAME}"')
        expire_record = self.get_expire_record()
        self.assertIsNone(expire_record.datetime_deleted)

    @patch('endorsement.management.commands.expire_shared_drives.logger')
    def test_expire_shared_drives(self, mock_logger):
        expire_record = self.get_expire_record()
        original_drive_name = expire_record.shared_drive.drive_name

        _output = self.call_command("--commit")
        mock_logger.info.assert_called_with(
            f'Expiring: {self.DRIVE_ID} "{self.DRIVE_NAME}"')

        expire_record = self.get_expire_record()
        self.assertIsNotNone(expire_record.datetime_deleted)
        self.assertTrue(
            original_drive_name != expire_record.shared_drive.drive_name)

    def test_expire_shared_drives_csv(self):
        output = self.call_command("--dump_drive_csv")
        expire_record = self.get_expire_record()
        self.assertIsNone(expire_record.datetime_deleted)
        self.assertIn("Drive ID,Drive Name,Manager NetIDs", output)
        self.assertIn(self.DRIVE_ID, output)
        self.assertIn(self.DRIVE_NAME, output)
