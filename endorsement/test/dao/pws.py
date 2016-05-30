from django.test import TestCase
from endorsement.dao.pws import _get_person, get_regid, is_valid_endorsee


FDAO_PWS = 'restclients.dao_implementation.pws.File'


class TestPwsDao(TestCase):

    def test_invalid_netid(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FDAO_PWS):
            self.assertFalse(is_valid_endorsee("notarealnetid"))

    def test_err_case(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FDAO_PWS):
            self.assertFalse(is_valid_endorsee("nomockid"))

    def test_normal_case(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FDAO_PWS):

            self.assertTrue(is_valid_endorsee('jstaff'))
            self.assertTrue(is_valid_endorsee('jfaculty'))

            self.assertEquals(get_regid('jstaff'),
                              "10000000000000000000000000000001")
            self.assertEquals(get_regid('jfaculty'),
                              "10000000000000000000000000000002")
