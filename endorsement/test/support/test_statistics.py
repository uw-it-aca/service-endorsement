from endorsement.test.support import SupportApiTest


class TestSupportStatistics(SupportApiTest):
    @property
    def reverse_id(self):
        return 'endorsement_statistics'

    def test_statistics(self):
        self._test_good_page()

    def test_bogus_user_statistics(self):
        self._test_invalid_user()
