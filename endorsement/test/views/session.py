from endorsement.test.views import require_url, TestViewApi
from endorsement.views.session import log_session_key


@require_url('home', 'endorsement urls not configured')
class TestLogSession(TestViewApi):

    def test_normal_cases(self):
        request = self.get_request('/', 'jstaff')
        session_key = log_session_key(request)
        self.assertIsNotNone(session_key)
