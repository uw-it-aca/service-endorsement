from django.test import TransactionTestCase
from endorsement.models.core import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import (
    store_office365_endorsement, store_google_endorsement,
    get_endorsements_by_endorser, is_office365_permitted,
    is_google_permitted)


class TestEndorseDao(TransactionTestCase):

    def test_store_endorsement(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee2')
        en = store_office365_endorsement(endorser, endorsee, None, 'because')
        self.assertEqual(en.category_code,
                         EndorsementRecord.OFFICE_365_ENDORSEE)
        self.assertEqual(en.endorser.netid, 'jstaff')
        self.assertEqual(en.endorsee.netid, 'endorsee2')

        self.assertEqual(en.category_code,
                         EndorsementRecord.OFFICE_365_ENDORSEE)
        self.assertEqual(en.endorser.netid, 'jstaff')
        self.assertEqual(en.endorsee.netid, 'endorsee2')

        en = store_google_endorsement(endorser, endorsee, None, 'because')
        self.assertEqual(en.category_code,
                         EndorsementRecord.GOOGLE_SUITE_ENDORSEE)

        self.assertIsNotNone(
            len(EndorsementRecord.objects.filter(endorser=endorser,
                                                 endorsee=endorsee,
                                                 is_deleted__isnull=True)))

        qset = EndorsementRecord.objects.filter(endorser=endorser,
                                                endorsee=endorsee,
                                                is_deleted__isnull=True)
        self.assertEqual(len(qset), 2)

        endorsee = get_endorsee_model('endorsee6')
        en = store_office365_endorsement(endorser, endorsee, None, 'because')
        self.assertEqual(en.category_code,
                         EndorsementRecord.OFFICE_365_ENDORSEE)
        self.assertEqual(en.endorser.netid, 'jstaff')
        self.assertEqual(en.endorsee.netid, 'endorsee6')

        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), 3)

        endorser = get_endorser_model('jfaculty')
        qset = get_endorsements_by_endorser(endorser)
        self.assertEqual(len(qset), 0)

    def test_is_o365_permitted(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee2')

        self.assertTrue(is_office365_permitted(
            endorser, endorsee), 0)

        self.assertTrue(is_google_permitted(
            endorser, endorsee), 0)
