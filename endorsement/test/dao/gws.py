from django.test import TestCase
from restclients.exceptions import DataFailureException
from restclients.exceptions import InvalidNetID
from endorsement.dao.gws import is_valid_endorser


FDAO = 'restclients.dao_implementation.gws.File'


class TestGwsDao(TestCase):

    def test_normal_cases(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FDAO):
            self.assertTrue(is_valid_endorser('jstaff'))
            self.assertTrue(is_valid_endorser('jfaculty'))

    def test_invalid_netid(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FDAO):
            self.assertFalse(is_valid_endorser("notarealnetid"))

    def test_err_case(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FDAO):
            self.assertFalse(is_valid_endorser("nomockid"))
