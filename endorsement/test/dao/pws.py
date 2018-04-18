from restclients_core.exceptions import (
    DataFailureException, InvalidNetID)
from endorsement.dao.pws import is_renamed_uwnetid,\
    get_endorser_data, get_endorsee_data
from endorsement.test.dao import TestDao


class TestPwsDao(TestDao):

    def test_is_renamed_uwnetid(self):
        self.assertRaises(InvalidNetID,
                          get_endorsee_data,
                          "notareal_uwnetid")
        self.assertFalse(is_renamed_uwnetid("nomockid"))
        self.assertFalse(is_renamed_uwnetid("endorsee1"))
        self.assertFalse(is_renamed_uwnetid("endorsee2"))
        self.assertFalse(is_renamed_uwnetid("endorsee3"))
        self.assertFalse(is_renamed_uwnetid("endorsee4"))
        self.assertTrue(is_renamed_uwnetid("endorsee5"))

    def test_get_endorsee_data(self):
        uwregid, display_anme, email = get_endorsee_data("endorsee1")
        self.assertEqual(uwregid, "50000000000000000000000000000001")
        self.assertEqual(display_anme, "Endorsee I")

        self.assertRaises(InvalidNetID,
                          get_endorsee_data,
                          "notareal_uwnetid")
        self.assertRaises(DataFailureException,
                          get_endorsee_data,
                          "nomockid")

    def test_get_endorser_data(self):
        regid, display_name = get_endorser_data('jstaff')
        self.assertEqual(regid,
                         "10000000000000000000000000000001")
        regid, display_name = get_endorser_data('jfaculty')
        self.assertEqual(regid,
                         "10000000000000000000000000000002")
        self.assertRaises(InvalidNetID,
                          get_endorser_data,
                          "notareal_uwnetid")
        self.assertRaises(DataFailureException,
                          get_endorser_data,
                          "nomockid")
