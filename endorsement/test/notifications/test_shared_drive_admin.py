# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.core import mail
from endorsement.test.notifications import NotificationsTestCase
from endorsement.notifications.shared_drive import (
    notify_admin_missing_drive_count_exceeded,
    notify_admin_over_quota_missing_subscription)


class TestSharedDriveAdminNotices(NotificationsTestCase):
    def test_admin_alert_notice(self):
        notify_admin_missing_drive_count_exceeded(
            missing_drive_count=101,
            missing_drive_notification=50,
            missing_drive_threshold=99)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertTrue("jstaff@uw.edu" in mail.outbox[0].to)
        self.assertTrue("99" in mail.outbox[0].body)
        self.assertTrue("101" in mail.outbox[0].body)

        notify_admin_over_quota_missing_subscription(
            drive_name="My Test Drive",
            drive_id="ABC123",
            quota_correct=400)

        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(len(mail.outbox[1].to), 1)
        self.assertTrue("jstaff@uw.edu" in mail.outbox[1].to)
        self.assertTrue("ABC123" in mail.outbox[1].body)

    def test_admin_warning_notice(self):
        notify_admin_missing_drive_count_exceeded(
            missing_drive_count=51,
            missing_drive_notification=50,
            missing_drive_threshold=100)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertTrue("jstaff@uw.edu" in mail.outbox[0].to)
        self.assertFalse("URGENT" in mail.outbox[0].subject)
        self.assertTrue("51" in mail.outbox[0].body)
