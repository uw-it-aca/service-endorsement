from endorsement.services import endorsement_services
from endorsement.dao.uwnetid_supported import (
    get_shared_netids_for_netid, valid_supported_resource)
from endorsement.test.dao import TestDao


class TestNetidSupported(TestDao):

    def test_get_shared_netids_for_netid(self):
        shared = get_shared_netids_for_netid('jstaff')
        self.assertEqual(len(shared), 16)

    def test_shared_valid_supported_resource(self):
        for shared in get_shared_netids_for_netid('jstaff'):
            for service in endorsement_services():
                valid = valid_supported_resource(shared, service)
                if service.service_name == 'canvas':
                    self.assertEqual(
                        valid, shared.netid_type == 'administrator')
                elif service.service_name in ['o365', 'google']:
                    self.assertEqual(valid, (shared.name != 'pppmsrv'))
                else:
                    raise Exception("Missing shared netid service test")
