from django.test import TestCase
from restclients.exceptions import DataFailureException
from restclients.exceptions import InvalidNetID
from endorsement.dao.gws import gws


FDAO_GWS = 'restclients.dao_implementation.gws.File'


class TestGwsDao(TestCase):

    def test_is_staff(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FDAO_GWS):
            self.assertTrue(gws.is_effective_member('uw_staff',
                                                    'jstaff'))
            self.assertFalse(gws.is_effective_member('uw_staff',
                                                     'jfaculty'))

    def test_is_faculty(self):
        with self.settings(RESTCLIENTS_GWS_DAO_CLASS=FDAO_GWS):
            self.assertFalse(gws.is_effective_member('uw_faculty',
                                                     'jstaff'))
            self.assertTrue(gws.is_effective_member('uw_faculty',
                                                    'jfaculty'))
