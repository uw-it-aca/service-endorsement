# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.test.services import ServicesApiTest
from endorsement.services import get_endorsement_service


class TestHuskyOnNetAffiliateService(ServicesApiTest):
    @property
    def service(self):
        return get_endorsement_service('husky-onnet-affiliate')

    def test_valid_endorser(self):
        self.assertTrue(self.service.valid_endorser('jstaff'))
        self.assertTrue(self.service.valid_endorser('jfaculty'))

        self.assertFalse(self.service.valid_endorser("notareal_uwnetid"))
        self.assertFalse(self.service.valid_endorser("nomockid"))

        # test exception
        self.assertRaises(Exception, self.service.valid_endorser, None)

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
        self.assertEquals(len(endorsible), 0)
        self.assertEquals(len(endorsed), 0)
        self.assertFalse('cpnebeng' in endorsible)
        self.assertFalse('wadm_jstaff' in endorsed)

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

        self.assertEqual(len(endorsible), 0)
        self.assertEqual(len(endorsing), 0)
        self.assertEqual(len(endorsed), 0)
        self.assertEqual(len(errored), 2)
