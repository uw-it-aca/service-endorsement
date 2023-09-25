# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from unittest.mock import MagicMock, patch
from django.urls import reverse
from django.core.management import call_command
from django.test import Client
from userservice.user import get_original_user
from endorsement.test.views import require_url, TestViewApi
from endorsement.models import (
    Accessee, Accessor, AccessRight, AccessRecord, AccessRecordConflict)


@require_url('access_right_resolve_api', 'access urls not configured')
class TestResolve(TestViewApi):

    def setUp(self):
        super(TestResolve, self).setUp()

        # seed db
        call_command('loaddata', 'test_data/accessright.json')
        call_command('loaddata', 'test_data/accessee.json')
        call_command('loaddata', 'test_data/accessor.json')
        call_command('loaddata', 'test_data/accessrecordconflict.json')

    @patch('endorsement.views.api.office.resolve.revoke_access')
    def test_resolve_api(self, mock_revoke_delegate):
        test_request = {
            'access_type': "FullAccess",
            'delegate': "u_javerage_admin",
            'mailbox': "jstaff"
        }

        self.assertEqual(0, AccessRecord.objects.all().count())
        self.assertEqual(1, AccessRecordConflict.objects.all().count())

        request = self.get_request('/', 'jstaff')
        response = self.post_response('access_right_resolve_api', test_request)

        mock_revoke_delegate.assert_called_once()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, AccessRecord.objects.all().count())
        self.assertEqual(0, AccessRecordConflict.objects.all().count())
