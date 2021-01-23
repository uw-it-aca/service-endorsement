from django.test import TransactionTestCase
from endorsement.models.core import EndorsementRecord
from endorsement.services import ENDORSEMENT_SERVICES
from endorsement.dao.user import get_endorser_model, get_endorsee_model
import random
from endorsement.dao.endorse import get_endorsements_by_endorser, is_endorsed


class TestEndorseDao(TransactionTestCase):

    def test_endorsement_store_and_clear(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee2')

        for service_tag, svc in ENDORSEMENT_SERVICES.items():
            en = svc['store'](endorser, endorsee, None, 'because')

            self.assertEqual(en.category_code, svc['category_code'])
            self.assertEqual(en.endorser.netid, 'jstaff')
            self.assertEqual(en.endorsee.netid, 'endorsee2')

        self.assertIsNotNone(
            len(EndorsementRecord.objects.filter(endorser=endorser,
                                                 endorsee=endorsee,
                                                 is_deleted__isnull=True)))

        qset = EndorsementRecord.objects.filter(endorser=endorser,
                                                endorsee=endorsee,
                                                is_deleted__isnull=True)
        self.assertEqual(len(qset), len(ENDORSEMENT_SERVICES))

        # test udpate
        svc_key = random.choice(list(ENDORSEMENT_SERVICES.keys()))
        svc = ENDORSEMENT_SERVICES[svc_key]
        en = svc['clear'](endorser, endorsee)
        self.assertEqual(en.category_code, svc['category_code'])

        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), len(ENDORSEMENT_SERVICES) - 1)

        endorsee = get_endorsee_model('endorsee6')
        en = svc['store'](endorser, endorsee, None, 'because')
        self.assertEqual(en.category_code, svc['category_code'])
        self.assertEqual(en.endorser.netid, 'jstaff')
        self.assertEqual(en.endorsee.netid, 'endorsee6')

        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), len(ENDORSEMENT_SERVICES))

        endorser = get_endorser_model('jfaculty')
        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), 0)

    def test_is_permitted(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee2')

        for service_tag, svc in ENDORSEMENT_SERVICES.items():
            self.assertFalse(svc['permitted'](endorser, endorsee)[0])

    def test_is_endorsed(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        svc_key = 'o365'
        svc = ENDORSEMENT_SERVICES[svc_key]
        en = svc['store'](endorser, endorsee, None, 'because')
        self.assertTrue(is_endorsed(en))

        endorsee = get_endorsee_model('endorsee3')
        en = svc['store'](endorser, endorsee, None, 'because')
        self.assertFalse(is_endorsed(en))
