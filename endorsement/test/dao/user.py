from django.test import TestCase, TransactionTestCase
from restclients.exceptions import DataFailureException
from endorsement.models.core import Endorser, Endorsee
from endorsement.dao.user import get_endorser_model, get_endorsee_model


class TestUserDao(TransactionTestCase):

    def test_get_endorser_model(self):
        user, created = get_endorser_model('jstaff')
        self.assertIsNotNone(user)
        self.assertEqual(user.regid,
                         '10000000000000000000000000000001')
        self.assertTrue(user.is_valid)

        qset = Endorser.objects.filter(netid='jstaff')
        self.assertEqual(len(qset), 1)

        self.assertIsNotNone(Endorser.objects.get(netid='jstaff'))

    def test_get_endorsee_model(self):
        user, created = get_endorsee_model('endorsee1')
        self.assertIsNotNone(user)
        self.assertEqual(user.display_name, "Endorsee I")
        self.assertTrue(user.kerberos_active_permitted)

        qset = Endorsee.objects.filter(netid='endorsee1')
        self.assertEqual(len(qset), 1)

        self.assertIsNotNone(Endorsee.objects.get(netid='endorsee1'))

        self.assertRaises(DataFailureException,
                          get_endorsee_model,
                          'endorsee5')
        qset = Endorsee.objects.filter(netid='endorsee5')
        self.assertEqual(len(qset), 0)
