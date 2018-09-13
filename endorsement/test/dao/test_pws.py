from restclients_core.exceptions import InvalidNetID
from endorsement.dao.pws import is_renamed_uwnetid,\
    get_endorser_data, get_endorsee_data
from endorsement.exceptions import UnrecognizedUWNetid
from endorsement.test.dao import TestDao


class TestPwsDao(TestDao):

    def test_is_renamed_uwnetid(self):
        self.assertRaises(InvalidNetID,
                          get_endorsee_data,
                          "0notareal_uwnetid")
        self.assertFalse(is_renamed_uwnetid("nomockid"))
        self.assertFalse(is_renamed_uwnetid("endorsee1"))
        self.assertFalse(is_renamed_uwnetid("endorsee2"))
        self.assertFalse(is_renamed_uwnetid("endorsee3"))
        self.assertFalse(is_renamed_uwnetid("endorsee4"))
        self.assertTrue(is_renamed_uwnetid("endorsee5"))

    def test_get_endorsee_data(self):
        uwregid, display_anme, email, is_person = get_endorsee_data(
            "endorsee2")
        self.assertEqual(uwregid, "BE43A1115A014E5595703379511536E1")
        self.assertEqual(display_anme, "SIMON ENDORSEE2")
        self.assertEqual(email, "endorsee2@uw.edu")

        self.assertRaises(InvalidNetID,
                          get_endorsee_data,
                          "0notareal_uwnetid")
        self.assertRaises(UnrecognizedUWNetid,
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
                          "0notareal_uwnetid")
        self.assertRaises(UnrecognizedUWNetid,
                          get_endorser_data,
                          "nomockid")
