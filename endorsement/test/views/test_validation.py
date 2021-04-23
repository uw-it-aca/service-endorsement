# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from endorsement.test.views import TestViewApi
from endorsement.userservice_validation import validate, can_override_user


class TestNetIDValidation(TestViewApi):
    def test_can_override_netid(self):
        request = self.get_request('/', 'jstaff')
        self.assertFalse(can_override_user(request))

        request = self.get_request('/', 'jnone')
        self.assertFalse(can_override_user(request))
