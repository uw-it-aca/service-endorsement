# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.urls import reverse
from django.test import Client
from userservice.user import get_original_user
from endorsement.models import (
    Accessee, Accessor, AccessRight, AccessRecord, AccessRecordConflict)
from endorsement.test.views import require_url
from endorsement.test.api import EndorsementApiTest


@require_url('access_api', 'access url not configured')
class TestAccess(EndorsementApiTest):
    fixtures = ['test_data/accessright.json',
                'test_data/accessee.json',
                'test_data/accessor.json']

    def test_access_api(self):
        test_data = {
            'access_type': "FullAccess",
            'delegate': "u_javerage_admin",
            'mailbox': "jstaff"
        }

        self.assertEqual(0, AccessRecord.objects.all().count())

        self.set_user('jstaff')

        url = reverse('access_api')
        response = self.client.post(
            url, test_data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, AccessRecord.objects.all().count())

    def test_access_api_missing_param(self):
        test_data = {
            'access_type': "FullAccess",
            'delegate': "u_javerage_admin",
            'mailbox': None
        }

        self.assertEqual(0, AccessRecord.objects.all().count())

        self.set_user('jstaff')

        url = reverse('access_api')
        response = self.client.post(
            url, test_data, content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(0, AccessRecord.objects.all().count())

    def test_access_api_renew(self):
        test_data = {
            'action': 'renew',
            'access_type': "FullAccess",
            'delegate': "u_javerage_admin",
            'mailbox': "jstaff"
        }

        self.assertEqual(0, AccessRecord.objects.all().count())

        self.set_user('jstaff')

        url = reverse('access_api')
        response = self.client.post(
            url, test_data, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, AccessRecord.objects.all().count())
