from endorsement.test.views import TestViewApi
from endorsement.userservice_validation import validate, can_override_user


class TestNetIDValidation(TestViewApi):
    def test_validate_netid(self):
        self.assertTrue(validate('jstaff') is None)
        self.assertFalse(validate('notavalid_user_netid') is None)
        self.assertFalse(validate('') is None)

    def test_can_override_netid(self):
        request = self.get_request('/', 'jstaff')
        self.assertFalse(can_override_user(request))

        request = self.get_request('/', 'jnone')
        self.assertFalse(can_override_user(request))
