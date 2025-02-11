# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from django.urls import reverse
from django.test import Client
from userservice.user import get_original_user
from endorsement.test.views import require_url, TestViewApi
from endorsement.models import (
    Accessee, Accessor, AccessRight, AccessRecord, AccessRecordConflict)


@require_url('access_right_resolve_api', 'access urls not configured')
class TestResolve(TestViewApi):
    fixtures = ['test_data/accessright.json',
                'test_data/accessee.json',
                'test_data/accessor.json',
                'test_data/accessrecordconflict.json']

    def test_resolve_api(self):
        test_request = {
            'access_type': "FullAccess",
            'delegate': "u_javerage_admin",
            'mailbox': "jstaff"
        }

        self.assertEqual(0, AccessRecord.objects.all().count())
        self.assertEqual(1, AccessRecordConflict.objects.all().count())

        request = self.get_request('/', 'jstaff')
        response = self.post_response('access_right_resolve_api', test_request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, AccessRecord.objects.all().count())
        self.assertEqual(0, AccessRecordConflict.objects.all().count())
