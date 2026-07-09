# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.models import SharedDriveRecord


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
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['drives']), 8)

    def test_no_shared_drives(self):
        self.set_user('jinter')
        url = reverse('shared_drive_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['drives']), 0)

    def test_shared_drive_deletion_rescue(self):
        drive_id = 'ABC_0123-DF56AA1234'
        record = SharedDriveRecord.objects.get(
            shared_drive__drive_id=drive_id)
        drive_name = record.shared_drive.drive_name

        self.set_user('jstaff')
        url = reverse('shared_drive_api', kwargs={
            'drive_id': drive_id})
        data = json.dumps({"accept": True})
        response = self.client.put(
            url, data=data, content_type='application/json')

        self.assertEqual(response.status_code, 200)

        record = SharedDriveRecord.objects.get(
            shared_drive__drive_id=drive_id)
        self.assertTrue(drive_name != record.shared_drive.drive_name)
