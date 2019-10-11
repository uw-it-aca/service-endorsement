from django.test import TestCase
from django.utils import timezone
from django.core import mail
from django.db.models import F
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.policy import (
    _endorsements_to_warn, _endorsements_to_expire,
    DEFAULT_ENDORSEMENT_LIFETIME, DEFAULT_ENDORSEMENT_GRACETIME,
    NOTICE_1_DAYS_PRIOR, NOTICE_2_DAYS_PRIOR,
    NOTICE_3_DAYS_PRIOR, NOTICE_4_DAYS_PRIOR)
from endorsement.dao.notification import warn_endorsers
from datetime import timedelta


class TestProvisioneExpirationNotices(TestCase):
    def setUp(self):
        now = timezone.now() - timedelta(hours=1)
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
        # expire date long ago
        EndorsementRecord.objects.create(
            endorser=self.endorser1, endorsee=self.endorsee1,
            category_code=EndorsementRecord.OFFICE_365_ENDORSEE,
            reason="Just Because",
            datetime_endorsed=now - timedelta(days=(
                DEFAULT_ENDORSEMENT_LIFETIME + 200)))
        # expire date today
        EndorsementRecord.objects.create(
            endorser=self.endorser1, endorsee=self.endorsee1,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
            reason="Just Because",
            datetime_endorsed=now - timedelta(days=(
                DEFAULT_ENDORSEMENT_LIFETIME)))
        # expire date tomorrow
        EndorsementRecord.objects.create(
            endorser=self.endorser2, endorsee=self.endorsee2,
            category_code=EndorsementRecord.OFFICE_365_ENDORSEE,
            reason="I said so",
            datetime_endorsed=now - timedelta(days=(
                DEFAULT_ENDORSEMENT_LIFETIME - 1)))

    def _notice_and_expire(self, now, expected):
        endorsements = _endorsements_to_expire(now)
        self.assertEqual(len(endorsements), expected[0])

        endorsements = _endorsements_to_warn(now, 1)
        self.assertEqual(len(endorsements), expected[1])
        endorsements.update(datetime_notice_1_emailed=now)

        endorsements = _endorsements_to_warn(now, 2)
        self.assertEqual(len(endorsements), expected[2])
        endorsements.update(datetime_notice_2_emailed=now)

        endorsements = _endorsements_to_warn(now, 3)
        self.assertEqual(len(endorsements), expected[3])
        endorsements.update(datetime_notice_3_emailed=now)

        endorsements = _endorsements_to_warn(now, 4)
        self.assertEqual(len(endorsements), expected[4])
        endorsements.update(datetime_notice_4_emailed=now)

    def test_expiration_and_notices(self):
        # notice one days prior to expiration: two first notices, no expirations
        now = timezone.now() - timedelta(days=NOTICE_1_DAYS_PRIOR)
        self._notice_and_expire(now, [0, 2, 0, 0, 0])

        # next day: one first notice, no expirations
        self._notice_and_expire(now + timedelta(days=1), [0, 1, 0, 0, 0])

        # 30 days later: no notices, no expiration
        self._notice_and_expire(now + timedelta(days=30), [0, 0, 0, 0, 0])

        # notice two days prior: two second notices, no expiration
        now += timedelta(days=NOTICE_1_DAYS_PRIOR - NOTICE_2_DAYS_PRIOR + 1)
        self._notice_and_expire(now, [0, 0, 2, 0, 0])

        # next day: one second notice, no expiration
        self._notice_and_expire(now + timedelta(days=1), [0, 0, 1, 0, 0])

        # next day: no notice, no expiration
        self._notice_and_expire(now + timedelta(days=2), [0, 0, 0, 0, 0])

        # notice three days prior: two third notices, no expiration
        now += timedelta(days=NOTICE_2_DAYS_PRIOR - NOTICE_3_DAYS_PRIOR + 1)
        self._notice_and_expire(now, [0, 0, 0, 2, 0])

        # next day: one third notice, no expiration
        self._notice_and_expire(now + timedelta(days=1), [0, 0, 0, 1, 0])

        # next day: no notices, no expiration
        self._notice_and_expire(now + timedelta(days=2), [0, 0, 0, 0, 0])

        # expiration day: two fourth notices, no expiration
        now += timedelta(days=NOTICE_3_DAYS_PRIOR - NOTICE_4_DAYS_PRIOR + 1)
        self._notice_and_expire(now, [0, 0, 0, 0, 2])

        # next day: one fourth notices, no expiration
        self._notice_and_expire(now + timedelta(days=1), [0, 0, 0, 0, 1])

        # 89 days forward: no notices, no expiration
        now += timedelta(days=DEFAULT_ENDORSEMENT_GRACETIME)
        self._notice_and_expire(now, [0, 0, 0, 0, 0])

        # next day forward: no notices, two expirations
        now += timedelta(days=1)
        self._notice_and_expire(now, [2, 0, 0, 0, 0])

        # next day forward: no notices, three expirations
        now += timedelta(days=1)
        self._notice_and_expire(now, [3, 0, 0, 0, 0])

    def test_expiration_and_notice_email(self):
        warn_endorsers(1, DEFAULT_ENDORSEMENT_LIFETIME)
        self.assertEqual(len(mail.outbox), 2)
        print("Subject: {0}".format(mail.outbox[0].subject))
        print("Text: {0}".format(mail.outbox[0].body))
        print("HTML: {0}".format(mail.outbox[0].alternatives[0][0]))

        EndorsementRecord.objects.filter(
            datetime_notice_1_emailed__isnull=False).update(
                datetime_notice_1_emailed=F(
                    'datetime_notice_1_emailed')-timedelta(days=61))

        warn_endorsers(2, DEFAULT_ENDORSEMENT_LIFETIME)
        self.assertEqual(len(mail.outbox), 4)

        EndorsementRecord.objects.filter(
            datetime_notice_2_emailed__isnull=False).update(
                datetime_notice_2_emailed=F(
                    'datetime_notice_2_emailed')-timedelta(days=30))

        warn_endorsers(3, DEFAULT_ENDORSEMENT_LIFETIME)
        self.assertEqual(len(mail.outbox), 6)

        EndorsementRecord.objects.filter(
            datetime_notice_3_emailed__isnull=False).update(
                datetime_notice_3_emailed=F(
                    'datetime_notice_2_emailed')-timedelta(days=23))

        warn_endorsers(4, DEFAULT_ENDORSEMENT_LIFETIME)
        print("Subject: {0}".format(mail.outbox[-1].subject))
        print("Text: {0}".format(mail.outbox[-1].body))
        print("HTML: {0}".format(mail.outbox[-1].alternatives[0][0]))

        self.assertEqual(len(mail.outbox), 8)
