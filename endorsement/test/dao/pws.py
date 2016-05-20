from django.test import TestCase
from restclients.exceptions import DataFailureException
from restclients.exceptions import InvalidNetID
from endorsement.dao.pws import pws


FDAO_PWS = 'restclients.dao_implementation.pws.File'


class TestPwsDao(TestCase):

    def test_not_in_pws_netid(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FDAO_PWS):
            self.assertRaises(InvalidNetID,
                              pws.get_person_by_netid,
                              "notarealnetid")

    def test_pws_err(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FDAO_PWS):
            self.assertRaises(DataFailureException,
                              pws.get_person_by_netid,
                              "nomockid")

    def test_get_person(self):
        with self.settings(RESTCLIENTS_PWS_DAO_CLASS=FDAO_PWS):
            staff_person = pws.get_person_by_netid('jstaff')
            self.assertTrue(staff_person.is_staff)
            self.assertFalse(staff_person.is_faculty)
            self.assertEquals(staff_person.uwregid,
                              "10000000000000000000000000000001")

            faculty_person = pws.get_person_by_netid('jfaculty')
            self.assertTrue(faculty_person.is_faculty)
            self.assertFalse(faculty_person.is_staff)
            self.assertEquals(faculty_person.uwregid,
                              "10000000000000000000000000000002")
