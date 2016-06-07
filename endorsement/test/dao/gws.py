from restclients.exceptions import DataFailureException
from restclients.exceptions import InvalidNetID
from endorsement.dao.gws import is_valid_endorser
from endorsement.test.dao import TestDao


class TestGwsDao(TestDao):

    def test_normal_cases(self):
        self.assertTrue(is_valid_endorser('jstaff'))
        self.assertTrue(is_valid_endorser('jfaculty'))

    def test_invalid_netid(self):
        self.assertFalse(is_valid_endorser("notarealnetid"))

    def test_err_case(self):
        self.assertFalse(is_valid_endorser("nomockid"))
