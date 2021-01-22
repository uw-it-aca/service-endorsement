from endorsement.dao.uwnetid_supported import (
    get_shared_netids_for_netid, shared_netid_in_excluded_category)
from endorsement.test.dao import TestDao


class TestNetidSupported(TestDao):

    def test_get_shared_netids_for_netid(self):
        shared = get_shared_netids_for_netid('jstaff')
        self.assertEqual(len(shared), 22)

    def test_shared_netid_in_excluded_category(self):
        for shared in get_shared_netids_for_netid('jstaff'):
            excluded = shared_netid_in_excluded_category(shared.name)
            self.assertEqual(excluded, (shared.name == 'pppmsrv'))
