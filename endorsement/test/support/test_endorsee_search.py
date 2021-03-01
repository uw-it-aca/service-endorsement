from endorsement.test.support import SupportApiTest


class TestSupportEndorseeSearch(SupportApiTest):
    @property
    def reverse_id(self):
        return 'endorsee_search'

    def test_statistics(self):
        self._test_good_page()

    def test_bogus_user_statistics(self):
        self._test_invalid_user()