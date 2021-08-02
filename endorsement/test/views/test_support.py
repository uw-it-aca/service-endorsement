# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.test import override_settings
from endorsement.test.views import TestViewApi
from django.urls import reverse
from endorsement.userservice_validation import can_override_user
from endorsement.views.support.endorsee_search import EndorseeSearch
from endorsement.views.support.endorser_search import EndorserSearch


class TestValidAdmin(TestViewApi):
    def test_valid_override(self):
        request = self.get_request(reverse('userservice_override'), 'jstaff')
        self.assertTrue(can_override_user(request))

    def test_invalid_override(self):
        request = self.get_request(reverse('userservice_override'), 'javerage')
        self.assertFalse(can_override_user(request))

        request = self.get_request(reverse('userservice_override'), 'foo@bar')
        self.assertFalse(can_override_user(request))

    def test_valid_endorsee_search(self):
        request = self.get_request(reverse('endorsee_search'), 'jstaff')
        response = EndorseeSearch.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_valid_endorser_search(self):
        request = self.get_request(reverse('endorser_search'), 'jstaff')
        response = EndorserSearch.as_view()(request)
        self.assertEqual(response.status_code, 200)


@override_settings(
    MOCK_SAML_ATTRIBUTES={
        'uwnetid': ['jstaff'],
        'isMemberOf': ['u_acadev_provision_support']})
class TestValidSupport(TestViewApi):
    def test_invalid_override(self):
        request = self.get_request(reverse('userservice_override'), 'jstaff')
        self.assertFalse(can_override_user(request))

    def test_valid_endorsee_search(self):
        request = self.get_request(reverse('endorsee_search'), 'jstaff')
        response = EndorseeSearch.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_invalid_endorsee_search(self):
        request = self.get_request(reverse('endorsee_search'), 'javerage')
        response = EndorseeSearch.as_view()(request)
        self.assertEqual(response.status_code, 401)

    def test_valid_endorser_search(self):
        request = self.get_request(reverse('endorser_search'), 'jstaff')
        response = EndorserSearch.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_invalid_endorser_search(self):
        request = self.get_request(reverse('endorser_search'), 'javerage')
        response = EndorserSearch.as_view()(request)
        self.assertEqual(response.status_code, 401)
