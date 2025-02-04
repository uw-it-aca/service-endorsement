# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.utils import timezone
from endorsement.models import Endorser, Endorsee, EndorsementRecord
from endorsement.endorsee_validation import validate_endorsees
from endorsement.services import endorsement_services
import binascii
import os


class TestProvisionerValidation(TestCase):
    def setUp(self):
        services = endorsement_services()
        service_count = len(services)

        self.assertTrue(service_count > 2)

        endorser = Endorser.objects.create(
            netid='jfaculty', regid='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            display_name='Dr J', is_valid=True)

        # endorsees for endorsee/service matrix
        endorsees = []
        for i in range(service_count):
            endorsees.append(Endorsee.objects.create(
                netid='endorsee{}'.format(i+1),
                regid=binascii.b2a_hex(os.urandom(16)),
                display_name='Endorsee {}'.format(i+1),
                is_person=True))

        now = timezone.now()
        delete = 0
        # per endorsee: skip one service, delete one, the rest valid
        for service in services:
            for i in range(service_count):
                if i != ((delete + 1) % service_count):
                    er = {
                        'endorser': endorser,
                        'endorsee': endorsees[i],
                        'category_code': service.category_code,
                        'reason': "I said so",
                        'datetime_endorsed': now
                    }

                    if delete == i:
                        er['is_deleted'] = True

                    EndorsementRecord.objects.create(**er)

            delete += 1

        # confirm proper setup
        self.assertEqual(
            EndorsementRecord.objects.all().count(),
            (service_count ** 2) - service_count)
        self.assertEqual(
            EndorsementRecord.objects.filter(is_deleted__isnull=False).count(),
            service_count)

    def test_validate_endorsees(self):
        services = endorsement_services()
        service_count = len(services)

        # mock data should clear endorsee1 and endorsee2 endorsements
        validate_endorsees()

        self.assertEqual(EndorsementRecord.objects.filter(
            endorsee__netid='endorsee1', is_deleted__isnull=False).count(),
                         service_count - 1)
        self.assertEqual(EndorsementRecord.objects.filter(
            endorsee__netid='endorsee2', is_deleted__isnull=False).count(),
                         service_count - 1)
        self.assertEqual(EndorsementRecord.objects.filter(
            endorsee__netid='endorsee3', is_deleted__isnull=True).count(),
                         service_count - 2)
