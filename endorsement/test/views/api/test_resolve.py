# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


from endorsement.models import AccessRecord, AccessRecordConflict
from endorsement.test.views import TestViewApi, require_url


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

        self.get_request('/', 'jstaff')
        response = self.post_response('access_right_resolve_api', test_request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, AccessRecord.objects.all().count())
        self.assertEqual(0, AccessRecordConflict.objects.all().count())
