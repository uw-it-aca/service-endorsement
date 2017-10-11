from django.test import TransactionTestCase
from endorsement.models.core import Endorser, EndorsementRecord
from endorsement.dao.migration import migrate_msca_endorsements


class TestMigration(TransactionTestCase):

    def test_migrate_msca_endorsements(self):
        endorsers, endorsements = migrate_msca_endorsements()
        self.assertEqual(endorsers, 2)
        qset = Endorser.objects.all()
        self.assertEqual(len(qset), 2)

        self.assertEqual(endorsements, 2)
        qset = EndorsementRecord.objects.all()
        self.assertEqual(len(qset), 2)
