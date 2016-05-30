from django.test import TestCase, TransactionTestCase
from django.conf import settings
from endorsement.models.user import Endorser
from endorsement.dao.user import get_endorser_model


class TestUserDao(TestCase):

    def test_get_endorser_model(self):
        user = get_endorser_model('jstaff')
        self.assertNotEquals(user, None)

        qset = Endorser.objects.filter(netid='jstaff')
        self.assertEqual(len(qset), 1)

        self.assertNotEquals(Endorser.objects.get(netid='jstaff'), None)
