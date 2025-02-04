# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest


class TestEndorsementEndorsedAPI(EndorsementApiTest):
    def test_none_endorsed(self):
        self.set_user('jfaculty')
        url = reverse('endorsed_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['endorsed']), 0)
