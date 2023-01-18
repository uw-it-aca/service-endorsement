# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.urls import reverse
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.test.api import EndorsementApiTest
import json


class ServicesApiTest(EndorsementApiTest):
    @property
    def service(self):
        return None

    def _test_endorsed(self):
        endorser = get_endorser_model('jstaff')
        endorsee1 = get_endorsee_model('endorsee2')
        endorsee2 = get_endorsee_model('endorsee6')
        self.service.initiate_endorsement(endorser, endorsee1, 'testing')
        self.service.store_endorsement(endorser, endorsee2, None, 'testing')

        self.set_user('jstaff')
        url = reverse('endorsed_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)

        endorsible, endorsing, endorsed, errored = self.get_endorsed(data)
        self.assertEquals(len(endorsible), 2)
        self.assertEquals(len(endorsing), 1)
        self.assertEquals(len(endorsed), 1)
        self.assertTrue(endorsee1.netid in endorsing)
        self.assertTrue(endorsee2.netid in endorsed)

    def _test_endorse(self, endorse_data):
        self.set_user('jstaff')
        url = reverse('endorse_api')

        response = self.client.post(
            url, json.dumps(endorse_data), content_type='application/json')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data['endorser']['is_valid'])
        self.assertEquals(data['endorser']['netid'], 'jstaff')

        return self.get_endorsed(data)

    def _test_endorse_netid(self):
        endorsible, endorsing, endorsed, errored = self._test_endorse({
            "endorsees": {
                "endorsee2": {
                    "name": "JERRY ENDORSEE2",
                    "email": "endorsee2@uw.edu",
                    self.service.service_name: {
                        "state": True,
                        "reason": "testing"
                    }
                }
            }
        })

        self.assertEqual(len(endorsible), 1)
        self.assertEqual(len(endorsing), 1)
        self.assertEqual(len(endorsed), 0)
        self.assertEqual(len(errored), 0)
        self.assertTrue('endorsee2' in endorsing)

    def get_shared(self, data):
        endorsible = []
        endorsed = []
        for shared in data['shared']:
            for service_name, v in shared['endorsements'].items():
                if service_name == self.service.service_name:
                    endorsible.append(shared['netid'])
                    if 'datetime_endorsed' in v:
                        self.assertFalse(v['datetime_endorsed'] is None)
                        endorsed.append(shared['netid'])
                else:
                    self.assertFalse('datetime_endorsed' in v)

        return endorsible, endorsed

    def get_endorsed(self, data):
        endorsible = []
        endorsing = []
        endorsed = []
        errored = []
        for netid, props in data['endorsed'].items():
            for service_name, v in props['endorsements'].items():
                if service_name == self.service.service_name:
                    if 'datetime_endorsed' in v:
                        endorsible.append(netid)
                        if v['datetime_endorsed'] is None:
                            endorsing.append(netid)
                        else:
                            endorsed.append(netid)
                    else:
                        self.assertTrue('error' in v)
                        errored.append(netid)
                else:
                    self.assertFalse('datetime_endorsed' in v)

        return endorsible, endorsing, endorsed, errored
