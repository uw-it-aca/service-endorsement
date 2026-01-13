# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.utils import timezone
from django.core import mail
from endorsement.dao.user import get_endorser_model
from endorsement.models import Endorsee, EndorsementRecord
from endorsement.shared_validation import validate_shared_endorsers


class TestProvisioneSharedNetidNotices(TestCase):
    def setUp(self):
        now = timezone.now()
        self.javerage = get_endorser_model('javerage')
        self.bill = get_endorser_model('bill')
        self.endorsee = Endorsee.objects.create(
            netid='emailinfo', regid='cccccccccccccccccccccccccccccccc',
            display_name='Email Info', is_person=False)
        # expire date today
        EndorsementRecord.objects.create(
            endorser=self.javerage, endorsee=self.endorsee,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
            reason="Just Because",
            datetime_endorsed=now)

    def test_shared_netid_owner_warning(self):
        validate_shared_endorsers()

        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(' Shared ' in mail.outbox[0].subject)
        self.assertTrue('emailinfo' in mail.outbox[0].body)
        self.assertTrue('emailinfo' in mail.outbox[0].alternatives[0][0])

        er_old = EndorsementRecord.objects.get(
            endorser=self.javerage, endorsee=self.endorsee,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE)

        self.assertEqual(er_old.is_deleted, True)

        er_new = EndorsementRecord.objects.get(
            endorser=self.bill, endorsee=self.endorsee,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE)

        self.assertEqual(er_new.is_deleted, None)

        self.assertEqual(er_old.datetime_notice_1_emailed,
                         er_new.datetime_notice_1_emailed)

    def test_shared_netid_owner_transfer(self):
        now = timezone.now()
        e_javerage = EndorsementRecord.objects.get(
            endorser=self.javerage, endorsee=self.endorsee,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE)
        self.assertEqual(e_javerage.is_deleted, None)
        e_bill = EndorsementRecord.objects.create(
            endorser=self.bill, endorsee=self.endorsee,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
            reason="Because I said so",
            datetime_endorsed=now)

        validate_shared_endorsers()

        self.assertEqual(len(mail.outbox), 0)

        e_javerage = EndorsementRecord.objects.get(
            endorser=self.javerage, endorsee=self.endorsee,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE)
        self.assertEqual(e_javerage.is_deleted, True)

        e_bill = EndorsementRecord.objects.get(
            endorser=self.bill, endorsee=self.endorsee,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE)
        self.assertEqual(e_bill.is_deleted, None)
