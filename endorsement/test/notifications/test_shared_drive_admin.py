# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.core import mail
from endorsement.test.notifications import NotificationsTestCase
from endorsement.notifications.shared_drive import (
    notify_admin_missing_drive_count_exceeded)


class TestSharedDriveAdminNotices(NotificationsTestCase):
    def test_admin_notices(self):
        notify_admin_missing_drive_count_exceeded(
            missing_drive_count=101,
            missing_drive_threshold=99)

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue("jstaff@uw.edu" in mail.outbox[0].to)
        self.assertTrue("99" in mail.outbox[0].body)
        self.assertTrue("101" in mail.outbox[0].body)
