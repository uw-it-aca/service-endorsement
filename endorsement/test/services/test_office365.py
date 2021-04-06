# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
import json
from django.urls import reverse
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.test.services import ServicesApiTest
from endorsement.services import get_endorsement_service


class TestOffice365Service(ServicesApiTest):
    @property
    def service(self):
        return get_endorsement_service('o365')

    def test_endorsed(self):
        self._test_endorsed()

    def test_shared(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('wadm_jstaff')

        self.assertEqual(len(
            EndorsementRecord.objects.get_endorsements_for_endorser(
                endorser)), 0)

        self.service.store_endorsement(endorser, endorsee, None, "for fun")

        self.set_user('jstaff')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data['endorser']['netid'] == 'jstaff')

        endorsible, endorsed = self.get_shared(data)
        self.assertEquals(len(endorsible), 12)
        self.assertEquals(len(endorsed), 1)
        self.assertTrue('cpnebeng' in endorsible)
        self.assertTrue('wadm_jstaff' in endorsed)

        # exlude category 22
        self.assertTrue('nebionotic' not in endorsible)

    def test_endorse_netid(self):
        self._test_endorse_netid()

    def test_endorse_shared(self):
        endorsible, endorsing, endorsed, errored = self._test_endorse({
            "endorsees": {
                # endorse valid shared
                "wadm_jstaff": {
                    "name": "ADMIN NETID JSTAFF",
                    "email": "wadm_jstaff@uw.edu",
                    "store": True,
                    self.service.service_name: {
                        "state": True,
                        "reason": "testing"
                    }
                },
                # endorse valid shared
                "cpnebeng": {
                    "name": "cpneb eng",
                    "email": "cpnebeng@uw.edu",
                    "store": True,
                    self.service.service_name: {
                        "state": True,
                        "reason": "testing"
                    }
                },
            }
        })

        self.assertEqual(len(endorsible), 2)
        self.assertEqual(len(endorsing), 0)
        self.assertEqual(len(endorsed), 2)
        self.assertEqual(len(errored), 0)
        self.assertTrue('wadm_jstaff' in endorsed)
        self.assertTrue('cpnebeng' in endorsed)
