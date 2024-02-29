# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest


class TestSharedDrivesAPI(EndorsementApiTest):
    fixtures = [
        'test_data/member.json',
        'test_data/role.json',
        'test_data/shared_drive_member.json',
        'test_data/shared_drive_quota.json',
        'test_data/shared_drive.json',
        'test_data/shared_drive_record.json'
    ]

    def test_shared_drives(self):
        self.set_user('jstaff')
        url = reverse('shared_drives_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['drives']), 3)

    def test_no_shared_drives(self):
        self.set_user('endorsee2')
        url = reverse('shared_drives_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['drives']), 0)
