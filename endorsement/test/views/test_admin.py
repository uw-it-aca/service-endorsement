# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.test import override_settings
from endorsement.test.views import TestViewApi
from django.urls import reverse
from endorsement.userservice_validation import can_override_user


@override_settings(
    MOCK_SAML_ATTRIBUTES={
        'uwnetid': ['jstaff'],
        'isMemberOf': ['u_acadev_provision_admin']})
class TestValidAdmin(TestViewApi):
    def test_valid_override(self):
        request = self.get_request(reverse('userservice_override'), 'jstaff')
        self.assertTrue(can_override_user(request))
