from endorsement.test.views import require_url, TestViewApi
from userservice.user import get_original_user


@require_url('home', 'endorsement urls not configured')
class TestPage(TestViewApi):

    def test_err_cases(self):
        request = self.get_request('/', 'jnone')
        self.assertEqual(get_original_user(request), 'jnone')
        response = self.get_response("home")

        self.assertEqual(response.status_code, 401)

    def test_normal_cases(self):
        request = self.get_request('/', 'jstaff')
        self.assertEqual(get_original_user(request), 'jstaff')

        response = self.get_response("home")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.get_response("logout")
        self.assertEqual(response.status_code, 302)
