# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.urls import reverse
from endorsement.test.api import EndorsementApiTest


class TestEndorsementSharedNetidsAPI(EndorsementApiTest):
    def test_invalid_shared_netids(self):
        self.set_user('endorsee7')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)
