# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.test import TransactionTestCase
from endorsement.models.core import EndorsementRecord
from endorsement.services import endorsement_services, get_endorsement_service
from endorsement.dao.user import get_endorser_model, get_endorsee_model
import random
from endorsement.dao.endorse import get_endorsements_by_endorser
from endorsement.dao.uwnetid_categories import is_endorsed


class TestEndorseDao(TransactionTestCase):

    def test_endorsement_store_and_clear(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee2')

        for service in endorsement_services():
            en = service.store_endorsement(endorser, endorsee, None, 'because')

            self.assertEqual(en.category_code, service.category_code)
            self.assertEqual(en.endorser.netid, 'jstaff')
            self.assertEqual(en.endorsee.netid, 'endorsee2')

        self.assertIsNotNone(
            len(EndorsementRecord.objects.filter(endorser=endorser,
                                                 endorsee=endorsee,
                                                 is_deleted__isnull=True)))

        qset = EndorsementRecord.objects.filter(endorser=endorser,
                                                endorsee=endorsee,
                                                is_deleted__isnull=True)
        self.assertEqual(len(qset), len(endorsement_services()))

        # test udpate
        service = random.choice(endorsement_services())
        en = service.clear_endorsement(endorser, endorsee)
        self.assertEqual(en.category_code, service.category_code)

        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), len(endorsement_services()) - 1)

        endorsee = get_endorsee_model('endorsee6')
        en = service.store_endorsement(endorser, endorsee, None, 'because')
        self.assertEqual(en.category_code, service.category_code)
        self.assertEqual(en.endorser.netid, 'jstaff')
        self.assertEqual(en.endorsee.netid, 'endorsee6')

        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), len(endorsement_services()))

        endorser = get_endorser_model('jfaculty')
        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), 0)

    def test_is_permitted(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee2')

        for service in endorsement_services():
            self.assertFalse(service.is_permitted(endorser, endorsee)[0])

    def test_is_endorsed(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')
        service = get_endorsement_service('o365')

        en = service.store_endorsement(endorser, endorsee, None, 'because')
        self.assertTrue(is_endorsed(en))

        endorsee = get_endorsee_model('endorsee3')
        en = service.store_endorsement(endorser, endorsee, None, 'because')
        self.assertFalse(is_endorsed(en))
