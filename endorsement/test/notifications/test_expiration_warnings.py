# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.core import mail
from django.db.models import F
from django.utils import timezone
from endorsement.test.notifications import NotificationsTestCase
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.policy.endorsement import (
    _endorsements_to_warn, _endorsements_to_expire)
from endorsement.services import get_endorsement_service
from endorsement.notifications.endorsement import warn_endorsers
from datetime import timedelta


class TestProvisioneExpirationNotices(NotificationsTestCase):
    def setUp(self):
        self.now = timezone.now()

        self.endorser1 = Endorser.objects.create(
            netid='endorser1', regid='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            display_name='Not Valid', is_valid=True)
        self.endorser2 = Endorser.objects.create(
            netid='endorser2', regid='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            display_name='Not Valid', is_valid=True)
        self.endorsee1 = Endorsee.objects.create(
            netid='endorsee1', regid='cccccccccccccccccccccccccccccccc',
            display_name='Endorsee Six', is_person=True)
        self.endorsee2 = Endorsee.objects.create(
            netid='endorsee2', regid='dddddddddddddddddddddddddddddddd',
            display_name='Endorsee Seven', is_person=True)

        # common lifecycle dates, two services to test combined email
        o365 = get_endorsement_service('o365')
        google = get_endorsement_service('google')

        self.assertEqual(o365.endorsement_lifetime,
                         google.endorsement_lifetime)

        self.lifetime = o365.endorsement_lifetime
        self.graceperiod = o365.endorsement_graceperiod

        # expire date long ago
        EndorsementRecord.objects.create(
            endorser=self.endorser1, endorsee=self.endorsee1,
            category_code=o365.category_code,
            reason="Just Because",
            datetime_endorsed=self.days_ago(self.lifetime + 200))


        # expire date today
        EndorsementRecord.objects.create(
            endorser=self.endorser1, endorsee=self.endorsee1,
            category_code=google.category_code, reason="Just Because",
            datetime_endorsed=self.days_ago(self.lifetime))

        # expire date tomorrow
        EndorsementRecord.objects.create(
            endorser=self.endorser2, endorsee=self.endorsee2,
            category_code=o365.category_code,
            reason="I said so",
            datetime_endorsed=self.days_ago(self.lifetime - 1))

    def notice_and_expire(self, offset_days, expected_results):
        self.notice_and_expire_test(
            _endorsements_to_expire, _endorsements_to_warn,
            offset_days, expected_results)

    def test_expiration_and_notices(self):
        service = get_endorsement_service('o365')

        # use first service to get lifecycle dates
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
            [0, 0, 0, 0, 1],  # four plus a day
            [0, 0, 0, 0, 0],  # four plus two days
            [0, 0, 0, 0, 0],  # grace minus a day
            [2, 0, 0, 0, 0],  # grace
            [1, 0, 0, 0, 0]]  # grace plus a day

        self.message_timing(
            service.endorsement_expiration_warning, expected_results)

    def test_expiration_and_notice_email(self):
        warn_endorsers(1)
        self.assertEqual(len(mail.outbox), 2)

        EndorsementRecord.objects.filter(
            datetime_notice_1_emailed__isnull=False).update(
                datetime_notice_1_emailed=F(
                    'datetime_notice_1_emailed')-timedelta(days=61))

        warn_endorsers(2)
        self.assertEqual(len(mail.outbox), 4)

        EndorsementRecord.objects.filter(
            datetime_notice_2_emailed__isnull=False).update(
                datetime_notice_2_emailed=F(
                    'datetime_notice_2_emailed')-timedelta(days=30))

        warn_endorsers(3)
        self.assertEqual(len(mail.outbox), 6)

        EndorsementRecord.objects.filter(
            datetime_notice_3_emailed__isnull=False).update(
                datetime_notice_3_emailed=F(
                    'datetime_notice_2_emailed')-timedelta(days=23))

        warn_endorsers(4)
        self.assertEqual(len(mail.outbox), 8)
