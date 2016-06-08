from endorsement.dao.pws import _get_person, get_regid, is_valid_endorsee
from endorsement.test.dao import TestDao


class TestPwsDao(TestDao):

    def test_invalid_netid(self):
        self.assertFalse(is_valid_endorsee("notarealnetid"))

    def test_err_case(self):
        self.assertFalse(is_valid_endorsee("nomockid"))
        self.assertFalse(is_valid_endorsee("endorsee1"))
        self.assertFalse(is_valid_endorsee("endorsee3"))
        self.assertFalse(is_valid_endorsee("endorsee4"))
        self.assertFalse(is_valid_endorsee("endorsee5"))

    def test_normal_case(self):
        self.assertFalse(is_valid_endorsee("endorsee2"))
        self.assertTrue(is_valid_endorsee('jstaff'))
        self.assertTrue(is_valid_endorsee('jfaculty'))

        self.assertEquals(get_regid('jstaff'),
                          "10000000000000000000000000000001")
        self.assertEquals(get_regid('jfaculty'),
                          "10000000000000000000000000000002")
