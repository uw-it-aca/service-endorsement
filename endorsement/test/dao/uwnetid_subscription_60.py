from django.test import TestCase
from restclients.exceptions import DataFailureException
from restclients.exceptions import InvalidNetID
from endorsement.dao.uwnetid_subscription_60 import is_current_staff,\
    is_current_faculty


FDAO = 'restclients.dao_implementation.uwnetid.File'


class TestSubs60Dao(TestCase):

    def test_is_staff(self):
        with self.settings(RESTCLIENTS_UWNETID_DAO_CLASS=FDAO):
            self.assertTrue(is_current_staff('jstaff'))
            self.assertFalse(is_current_staff('jfaculty'))

    def test_is_faculty(self):
        with self.settings(RESTCLIENTS_UWNETID_DAO_CLASS=FDAO):
            self.assertFalse(is_current_faculty('jstaff'))
            self.assertTrue(is_current_faculty('jfaculty'))
