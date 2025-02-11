# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.core import mail
from django.db.models import F
from django.utils import timezone
from endorsement.test.notifications import NotificationsTestCase
from endorsement.models import AccessRecord, Accessee, Accessor
from endorsement.policy.access import AccessPolicy
from endorsement.notifications.access import accessee_lifecycle_warning
from datetime import timedelta


class TestSharedDriveExpirationNotices(NotificationsTestCase):
    def setUp(self):
        self.now = timezone.now()
        self.policy = AccessPolicy()

        accessee1 = Accessee.objects.create(
            netid='accessee1', regid='dddddddddddddddddddddddddddddddd',
            display_name='Accessee One')
        accessee2 = Accessee.objects.create(
            netid='accessee2', regid='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee',
            display_name='Accessee Two')
        accessee3 = Accessee.objects.create(
            netid='accessee3', regid='ffffffffffffffffffffffffffffffff',
            display_name='Accessee Three')

        accessor1 = Accessor.objects.create(
            name='accessor1', display_name='Accessor One')
        accessor2 = Accessor.objects.create(
            name='accessor2', display_name='Accessor Two')
        accessor3 = Accessor.objects.create(
            name='accessor3', display_name='Accessor Three')

        # accepted date long ago
        AccessRecord.objects.create(
            accessor=accessor1, accessee=accessee1,
            datetime_granted=self.days_ago(self.policy.lifetime + 200))

        # expire date today
        AccessRecord.objects.create(
            accessor=accessor2, accessee=accessee2,
            datetime_granted=self.days_ago(self.policy.lifetime))

        # expire date tomorrow
        AccessRecord.objects.create(
            accessor=accessor3, accessee=accessee3,
            datetime_granted=self.days_ago(self.policy.lifetime - 1))

    def test_expiration_and_notices(self):
        expected_results = [
            [0, 2, 0, 0, 0],  # level one
            [0, 1, 0, 0, 0],  # one plus a day
            [0, 0, 0, 0, 0],  # two minus a day
            [0, 0, 2, 0, 0],  # level two
            [0, 0, 1, 0, 0],  # two plus a day
            [0, 0, 0, 0, 0],  # three minus a day
            [0, 0, 0, 2, 0],  # level three
            [0, 0, 0, 1, 0],  # three plus a day
            [0, 0, 0, 0, 0],  # four minus a day
            [0, 0, 0, 0, 2],  # level four
            [2, 0, 0, 0, 1],  # four plus a day
            [1, 0, 0, 0, 0],  # four plus two days
            [0, 0, 0, 0, 0],  # grace minus a day
            [0, 0, 0, 0, 0],  # grace
            [0, 0, 0, 0, 0]]  # grace plus a day

        self.message_timing(expected_results)

    def test_expiration_and_notice_email(self):
        accessee_lifecycle_warning(1)
        self.assertEqual(len(mail.outbox), 3)

        AccessRecord.objects.filter(
            datetime_notice_1_emailed__isnull=False).update(
                datetime_notice_1_emailed=F(
                    'datetime_notice_1_emailed')-timedelta(days=61))

        accessee_lifecycle_warning(2)
        self.assertEqual(len(mail.outbox), 6)

        AccessRecord.objects.filter(
            datetime_notice_2_emailed__isnull=False).update(
                datetime_notice_2_emailed=F(
                    'datetime_notice_2_emailed')-timedelta(days=30))

        accessee_lifecycle_warning(3)
        self.assertEqual(len(mail.outbox), 9)

        AccessRecord.objects.filter(
            datetime_notice_3_emailed__isnull=False).update(
                datetime_notice_3_emailed=F(
                    'datetime_notice_2_emailed')-timedelta(days=23))

        accessee_lifecycle_warning(4)
        self.assertEqual(len(mail.outbox), 12)
