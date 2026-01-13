# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest


class TestSharedDrivesAPI(EndorsementApiTest):
    fixtures = [
        'test_data/member.json',
        'test_data/role.json',
        'test_data/itbill_quantity.json',
        'test_data/itbill_provision.json',
        'test_data/itbill_subscription.json',
        'test_data/shared_drive_member.json',
        'test_data/shared_drive_quota.json',
        'test_data/shared_drive.json',
        'test_data/shared_drive_record.json'
    ]

    def test_shared_drives(self):
        self.set_user('jstaff')
        url = reverse('shared_drive_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['drives']), 7)

    def test_no_shared_drives(self):
        self.set_user('jinter')
        url = reverse('shared_drive_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['drives']), 0)
