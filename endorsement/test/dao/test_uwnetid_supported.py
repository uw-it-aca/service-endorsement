# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.services import endorsement_services
from endorsement.dao.uwnetid_supported import get_supported_resources_for_netid
from endorsement.dao.user import get_endorser_model
from endorsement.test.dao import TestDao


class TestNetidSupported(TestDao):

    def test_get_supported_netids_for_netid(self):
        endorser = get_endorser_model('jstaff')
        supported = get_supported_resources_for_netid(endorser.netid)
        self.assertEqual(len(supported), 23)

        netids = set()
        for s in supported:
            for service in endorsement_services():
                if service.valid_supported_netid(s, endorser):
                    netids.add(s.name)
                    break

        self.assertEqual(len(netids), 16)
