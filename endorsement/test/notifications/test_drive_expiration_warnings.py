# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.core import mail
from django.db.models import F
from django.utils import timezone
from endorsement.test.notifications import NotificationsTestCase
from endorsement.models import SharedDriveRecord
from endorsement.policy.shared_drive import SharedDrivePolicy
from endorsement.notifications.shared_drive import warn_members
from datetime import timedelta


class TestSharedDriveExpirationNotices(NotificationsTestCase):
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

    def setUp(self):
        self.now = timezone.now()
        self.policy = SharedDrivePolicy()

        # reset all mock dates
        SharedDriveRecord.objects.all().update(datetime_accepted=self.now)

        # accepted date long ago
        drive = SharedDriveRecord.objects.get(pk=1)
        drive.datetime_accepted = self.days_ago(self.policy.lifetime + 200)
        drive.save()

        # expire date today
        drive = SharedDriveRecord.objects.get(pk=2)
        drive.datetime_accepted = self.days_ago(self.policy.lifetime)
        drive.save()

        # expire date tomorrow
        drive = SharedDriveRecord.objects.get(pk=6)
        drive.datetime_accepted = self.days_ago(self.policy.lifetime - 1)
        drive.save()

    def test_expiration_and_notices(self):
        expected_results = [
            [0, 2, 0, 0, 0], # level one
            [0, 1, 0, 0, 0], # one plus a day
            [0, 0, 0, 0, 0], # two minus a day
            [0, 0, 2, 0, 0], # level two
            [0, 0, 1, 0, 0], # two plus a day
            [0, 0, 0, 0, 0], # three minus a day
            [0, 0, 0, 2, 0], # level three
            [0, 0, 0, 1, 0], # three plus a day
            [0, 0, 0, 0, 0], # four minus a day
            [0, 0, 0, 0, 2], # level four
            [2, 0, 0, 0, 1], # four plus a day
            [1, 0, 0, 0, 0], # four plus two days
            [0, 0, 0, 0, 0], # grace minus a day
            [0, 0, 0, 0, 0], # grace
            [0, 0, 0, 0, 0]] # grace plus a day

        self.message_timing(expected_results)

    def test_expiration_and_notice_email(self):
        warn_members(1)
        self.assertEqual(len(mail.outbox), 3)

        SharedDriveRecord.objects.filter(
            datetime_notice_1_emailed__isnull=False).update(
                datetime_notice_1_emailed=F(
                    'datetime_notice_1_emailed')-timedelta(days=61))

        warn_members(2)
        self.assertEqual(len(mail.outbox), 6)

        SharedDriveRecord.objects.filter(
            datetime_notice_2_emailed__isnull=False).update(
                datetime_notice_2_emailed=F(
                    'datetime_notice_2_emailed')-timedelta(days=30))

        warn_members(3)
        self.assertEqual(len(mail.outbox), 9)

        SharedDriveRecord.objects.filter(
            datetime_notice_3_emailed__isnull=False).update(
                datetime_notice_3_emailed=F(
                    'datetime_notice_2_emailed')-timedelta(days=23))

        warn_members(4)
        self.assertEqual(len(mail.outbox), 12)
