from django.test import TestCase, TransactionTestCase
from restclients.exceptions import DataFailureException
from endorsement.models.core import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import store_endorsement


class TestEndorseDao(TransactionTestCase):

    def test_store_endorsement(self):
        endorser, created = get_endorser_model('jstaff')
        endorsee, created = get_endorsee_model('endorsee1')
        en, created = store_endorsement(endorser, endorsee)

        qset = EndorsementRecord.objects.filter(endorser=endorser,
                                                endorsee=endorsee)
        self.assertEqual(len(qset), 1)

        self.assertIsNotNone(
            EndorsementRecord.objects.get(endorser=endorser,
                                          endorsee=endorsee))
