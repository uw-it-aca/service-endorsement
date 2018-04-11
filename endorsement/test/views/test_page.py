from endorsement.test.views import require_url, TestViewApi
from userservice.user import get_original_user
import re


@require_url('home', 'endorsement urls not configured')
class TestPage(TestViewApi):

    def test_err_cases(self):
        request = self.get_request('/', 'jnone')
        self.assertEqual(get_original_user(request), 'jnone')
        response = self.get_response("home")

        self.assertEqual(response.status_code, 200)
        c = re.match('.*<div class="(invalid-endorser)">.*',
                     response.content, re.DOTALL)
        self.assertEqual(c.lastindex, 1)

    def test_normal_cases(self):
        request = self.get_request('/', 'jstaff')
        self.assertEqual(get_original_user(request), 'jstaff')

        response = self.get_response("home")
        self.assertEqual(response.status_code, 200)
