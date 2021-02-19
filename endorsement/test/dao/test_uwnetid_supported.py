from endorsement.services import endorsement_services
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.test.dao import TestDao


class TestNetidSupported(TestDao):

    def test_get_supported_netids_for_netid(self):
        supported = get_supported_resources_for_netid('jstaff')
        self.assertEqual(len(supported), 23)

        netids = []
        for s in supported:
            for service in endorsement_services():
                if service.valid_supported_netid(s):
                    netids.append(s.name)
                    break

        self.assertEqual(len(netids), 15)
