# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import binascii
import os

from django.test import TestCase
from django.utils import timezone

from endorsement.endorsee_validation import validate_endorsees
from endorsement.models import Endorsee, EndorsementRecord, Endorser
from endorsement.services import endorsement_services


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
                netid=f'endorsee{i+1}',
                regid=binascii.b2a_hex(os.urandom(16)),
                display_name=f'Endorsee {i+1}',
                is_person=True))

        now = timezone.now()
        # per endorsee: skip one service, delete one, the rest valid
        for service_index, service in enumerate(services):
            for i in range(service_count):
                if i != ((service_index + 1) % service_count):
                    er = {
                        'endorser': endorser,
                        'endorsee': endorsees[i],
                        'category_code': service.category_code,
                        'reason': "I said so",
                        'datetime_endorsed': now
                    }

                    if service_index == i:
                        er['is_deleted'] = True

                    EndorsementRecord.objects.create(**er)

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
