# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.test import TestCase
from django.core import mail
from django.utils import timezone
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.provisioner_validation import validate_endorsers
from endorsement.services import endorsement_services


class TestProvisionerValidation(TestCase):
    def setUp(self):
        invalid_endorser = Endorser.objects.create(
            netid='notvalid', regid='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            display_name='Not Valid', is_valid=False)
        jstaff = Endorser.objects.create(
            netid='jstaff', regid='a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a',
            display_name='Not Valid', is_valid=True)
        endorsee1 = Endorsee.objects.create(
            netid='endorsee1', regid='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
            display_name='Endorsee One', is_person=True)
        endorsee2 = Endorsee.objects.create(
            netid='endorsee2', regid='cccccccccccccccccccccccccccccccc',
            display_name='Endorsee Too', is_person=True)
        now = timezone.now()
        for service in endorsement_services():
            EndorsementRecord.objects.create(
                endorser=invalid_endorser, endorsee=endorsee1,
                category_code=service.category_code,
                reason="Stale", datetime_endorsed=now)

            EndorsementRecord.objects.create(
                endorser=jstaff, endorsee=endorsee2,
                category_code=service.category_code,
                reason="Preserved", datetime_endorsed=now)

            svc_endorsee = Endorsee.objects.create(
                netid='endorsee{}'.format(service.category_code),
                regid='ccccccccccccccccccccccccccccc{}'.format(
                    service.category_code),
                display_name='Endorsee {}'.format(
                    service.category_code),
                is_person=True)

            EndorsementRecord.objects.create(
                endorser=invalid_endorser, endorsee=svc_endorsee,
                category_code=service.category_code,
                reason="Stale", datetime_endorsed=now)

            EndorsementRecord.objects.create(
                endorser=jstaff, endorsee=svc_endorsee,
                category_code=service.category_code,
                reason="Preserved", datetime_endorsed=now)

    def test_validate_endorsers(self):
        validate_endorsers()

        self.assertEqual(len(mail.outbox), 1)

        self.assertTrue(Endorser.objects.get(
            netid='notvalid').datetime_emailed is not None)

        self.assertTrue(Endorser.objects.get(
            netid='jstaff').datetime_emailed is None)

        services = [s.valid_endorser(
            'notvalid') for s in endorsement_services()]

        self.assertEqual(EndorsementRecord.objects.filter(
            is_deleted=True).count(), services.count(False) * 2)

        self.assertEqual(EndorsementRecord.objects.filter(
            is_deleted__isnull=True).count(),
                         ((len(services) * 2) + (services.count(True) * 2)))
