from django.test import TransactionTestCase
from endorsement.models.core import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import (
    store_office365_endorsement, get_endorsements_by_endorser)


class TestEndorseDao(TransactionTestCase):

    def test_store_endorsement(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee1')
        en = store_office365_endorsement(endorser, endorsee)
        self.assertEqual(en.subscription_code,
                         EndorsementRecord.OFFICE_365)
        self.assertEqual(en.endorser.netid, 'jstaff')
        self.assertEqual(en.endorsee.netid, 'endorsee1')

        self.assertIsNotNone(
            EndorsementRecord.objects.get(endorser=endorser,
                                          endorsee=endorsee))

        qset = EndorsementRecord.objects.filter(endorser=endorser,
                                                endorsee=endorsee)
        self.assertEqual(len(qset), 1)

        endorsee = get_endorsee_model('endorsee2')
        en = store_office365_endorsement(endorser, endorsee)
        self.assertEqual(en.subscription_code,
                         EndorsementRecord.OFFICE_365)
        self.assertEqual(en.endorser.netid, 'jstaff')
        self.assertEqual(en.endorsee.netid, 'endorsee2')

        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), 2)

        endorser = get_endorser_model('jfaculty')
        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), 0)
