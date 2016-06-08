from restclients.exceptions import DataFailureException
from restclients.exceptions import InvalidNetID
from endorsement.dao.gws import is_valid_endorser,\
    get_endorsees_by_endorser
from endorsement.test.dao import TestDao


class TestGwsDao(TestDao):

    def test_normal_cases(self):
        self.assertTrue(is_valid_endorser('jstaff'))
        self.assertTrue(is_valid_endorser('jfaculty'))

    def test_invalid_netid(self):
        self.assertFalse(is_valid_endorser("notarealnetid"))

    def test_err_case(self):
        self.assertFalse(is_valid_endorser("nomockid"))

    def test_get_endorsees_by_endorser(self):
        endorsee_list = get_endorsees_by_endorser('jstaff')
        self.assertEquals(len(endorsee_list), 2)
        self.assertEquals(endorsee_list[0], 'endorsee1')
        self.assertEquals(endorsee_list[1], 'endorsee2')

        endorsee_list = get_endorsees_by_endorser('jfaculty')
        self.assertEquals(len(endorsee_list), 0)
