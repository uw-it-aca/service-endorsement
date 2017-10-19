from endorsement.dao.uwnetid_subscription_60 import is_valid_endorsee,\
    get_kerberos_subs_status
from endorsement.test.dao import TestDao


class TestNetidSubs60Dao(TestDao):

    def test_invalid_netid(self):
        self.assertFalse(is_valid_endorsee("notareal_uwnetid"))

    def test_err_case(self):
        self.assertFalse(is_valid_endorsee("nomockid"))
        self.assertFalse(is_valid_endorsee("none"))
        self.assertFalse(is_valid_endorsee("none1"))

    def test_normal_case(self):
        self.assertTrue(is_valid_endorsee('endorsee1'))
        self.assertTrue(is_valid_endorsee('endorsee2'))
        self.assertTrue(is_valid_endorsee('endorsee3'))
        self.assertTrue(is_valid_endorsee('endorsee4'))
        self.assertFalse(is_valid_endorsee('endorsee5'))

    def test_get_kerberos_subs_status(self):
        status_name, permitted = get_kerberos_subs_status('endorsee1')
        self.assertEqual(status_name, "Active")
        self.assertTrue(permitted)

        status_name, permitted = get_kerberos_subs_status('endorsee5')
        self.assertEqual(status_name, "Inactive")
        self.assertTrue(permitted)

        status_name, permitted = get_kerberos_subs_status('none')
        self.assertEqual(status_name, "Unpermitted")
        self.assertFalse(permitted)

        status_name, permitted = get_kerberos_subs_status('none1')
        self.assertEqual(status_name, "Active")
        self.assertFalse(permitted)
