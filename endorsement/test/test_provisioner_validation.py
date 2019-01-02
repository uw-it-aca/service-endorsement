from django.test import TestCase
from django.core import mail
from django.utils import timezone
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.provisioner_validation import validate_endorsers


class TestProvisionerValidation(TestCase):
    def setUp(self):
        endorser = Endorser.objects.create(
            netid='notvalid', regid='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            display_name='Not Valid', is_valid=False)
        endorsee1 = Endorsee.objects.create(
            netid='endorsee1', regid='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            display_name='Endorsee Six', is_person=True)
        endorsee2 = Endorsee.objects.create(
            netid='endorsee2', regid='cccccccccccccccccccccccccccccccc',
            display_name='Endorsee Seven', is_person=True)
        endorsee3 = Endorsee.objects.create(
            netid='endorsee3', regid='dddddddddddddddddddddddddddddddd',
            display_name='Endorsee Seven', is_person=False)
        EndorsementRecord.objects.create(
            endorser=endorser, endorsee=endorsee1,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
            reason="Just Because",
            datetime_endorsed=timezone.now())
        EndorsementRecord.objects.create(
            endorser=endorser, endorsee=endorsee1,
            category_code=EndorsementRecord.OFFICE_365_ENDORSEE,
            reason="I said so",
            datetime_endorsed=timezone.now())
        EndorsementRecord.objects.create(
            endorser=endorser, endorsee=endorsee2,
            category_code=EndorsementRecord.OFFICE_365_ENDORSEE,
            reason="I said so",
            datetime_endorsed=timezone.now())
        EndorsementRecord.objects.create(
            endorser=endorser, endorsee=endorsee3,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE,
            reason="I said so",
            datetime_endorsed=timezone.now())

    def test_validate_endorsers(self):
        validate_endorsers()
        endorser = Endorser.objects.get(netid='notvalid')
        endorsee1 = Endorsee.objects.get(netid='endorsee1')
        endorsee2 = Endorsee.objects.get(netid='endorsee2')
        endorsee3 = Endorsee.objects.get(netid='endorsee3')

        self.assertEqual(len(mail.outbox), 1)
        print("Subject: {0}".format(mail.outbox[0].subject))
        print("Text: {0}".format(mail.outbox[0].body))
        print("HTML: {0}".format(mail.outbox[0].alternatives[0][0]))

        self.assertTrue(Endorser.objects.get(
            netid='notvalid').datetime_emailed is not None)

        self.assertTrue(EndorsementRecord.objects.get(
            endorser=endorser, endorsee=endorsee1,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE).is_deleted)

        self.assertTrue(EndorsementRecord.objects.get(
            endorser=endorser, endorsee=endorsee1,
            category_code=EndorsementRecord.OFFICE_365_ENDORSEE).is_deleted)

        self.assertTrue(EndorsementRecord.objects.get(
            endorser=endorser, endorsee=endorsee2,
            category_code=EndorsementRecord.OFFICE_365_ENDORSEE).is_deleted)

        self.assertFalse(EndorsementRecord.objects.get(
            endorser=endorser, endorsee=endorsee3,
            category_code=EndorsementRecord.GOOGLE_SUITE_ENDORSEE).is_deleted)
