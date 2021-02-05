from django.test import TestCase
from django.core import mail
from django.utils import timezone
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.provisioner_validation import validate_endorsers
from endorsement.services import endorsement_services


class TestProvisionerValidation(TestCase):
    def setUp(self):
        endorser = Endorser.objects.create(
            netid='notvalid', regid='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            display_name='Not Valid', is_valid=False)
        endorsee1 = Endorsee.objects.create(
            netid='endorsee1', regid='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            display_name='Endorsee One', is_person=True)
        now = timezone.now()
        for service in endorsement_services():
            EndorsementRecord.objects.create(
                endorser=endorser, endorsee=endorsee1,
                category_code=service.category_code,
                reason="Just Because", datetime_endorsed=now)

            EndorsementRecord.objects.create(
                endorser=endorser, endorsee=Endorsee.objects.create(
                    netid='endorsee{}'.format(service.category_code),
                    regid='ccccccccccccccccccccccccccccc{}'.format(
                        service.category_code),
                    display_name='Endorsee {}'.format(
                        service.category_code),
                    is_person=True),
                category_code=service.category_code,
                reason="I said so", datetime_endorsed=now)

    def test_validate_endorsers(self):
        validate_endorsers()
        endorser = Endorser.objects.get(netid='notvalid')
        endorsee1 = Endorsee.objects.get(netid='endorsee1')

        self.assertEqual(len(mail.outbox), 1)
        print("Subject: {0}".format(mail.outbox[0].subject))
        print("Text: {0}".format(mail.outbox[0].body))
        print("HTML: {0}".format(mail.outbox[0].alternatives[0][0]))

        self.assertTrue(Endorser.objects.get(
            netid='notvalid').datetime_emailed is not None)

        for service in endorsement_services():
            self.assertTrue(EndorsementRecord.objects.get(
                endorser=endorser, endorsee=endorsee1,
                category_code=service.category_code).is_deleted)

            self.assertTrue(EndorsementRecord.objects.get(
                endorser=endorser, endorsee=Endorsee.objects.get(
                    netid='endorsee{}'.format(service.category_code)),
                category_code=service.category_code).is_deleted)
