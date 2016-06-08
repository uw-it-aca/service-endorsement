from endorsement.dao.uwnetid_subscription_60 import is_valid_endorsee
from endorsement.test.dao import TestDao


class TestNetidSubs60Dao(TestDao):

    def test_invalid_netid(self):
        self.assertFalse(is_valid_endorsee("notarealnetid"))

    def test_err_case(self):
        self.assertFalse(is_valid_endorsee("nomockid"))

    def test_normal_case(self):
        self.assertTrue(is_valid_endorsee('endorsee1'))
        self.assertTrue(is_valid_endorsee('endorsee2'))
        self.assertTrue(is_valid_endorsee('endorsee3'))
        self.assertTrue(is_valid_endorsee('endorsee4'))
        self.assertTrue(is_valid_endorsee('endorsee5'))
