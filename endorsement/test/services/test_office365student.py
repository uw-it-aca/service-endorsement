# Copyright 2024 UW-IT, University of Washington
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
        return get_endorsement_service('o365student')

    def test_valid_endorser(self):
        self.assertTrue(self.service.valid_endorser('jstaff'))
        self.assertTrue(self.service.valid_endorser('jfaculty'))

        self.assertFalse(self.service.valid_endorser("notareal_uwnetid"))
        self.assertFalse(self.service.valid_endorser("nomockid"))

        # test exception
        self.assertRaises(Exception, self.service.valid_endorser, None)

    def test_endorsed(self):
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
        self.assertEquals(len(endorsible), 0)
        self.assertEquals(len(endorsing), 0)
        self.assertEquals(len(endorsed), 0)
        self.assertFalse(endorsee1.netid in endorsing)
        self.assertFalse(endorsee2.netid in endorsed)

    def test_shared(self):
        endorser = get_endorser_model('jstaff')
        bad_endorsee = get_endorsee_model('wadm_jstaff')
        good_endorsee = get_endorsee_model('emailinf')

        self.assertEqual(len(
            EndorsementRecord.objects.get_endorsements_for_endorser(
                endorser)), 0)

        self.service.store_endorsement(
            endorser, good_endorsee, None, "for fun")

        self.set_user('jstaff')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data['endorser']['netid'] == 'jstaff')

        endorsible, endorsed = self.get_shared(data)
        self.assertEquals(len(endorsible), 7)
        self.assertEquals(len(endorsed), 1)
        self.assertTrue('cpnebeng' in endorsible)
        self.assertTrue('phil123' in endorsible)
        self.assertFalse('wadm_jstaff' in endorsed)

        # exlude category 22
        self.assertTrue('nebionotic' not in endorsible)

    def test_endorse_netid(self):
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

        self.assertEqual(len(endorsible), 0)
        self.assertEqual(len(endorsing), 0)
        self.assertEqual(len(endorsed), 0)
        self.assertEqual(len(errored), 1)
        self.assertFalse('endorsee2' in endorsing)

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

        self.assertEqual(len(endorsible), 1)
        self.assertEqual(len(endorsing), 0)
        self.assertEqual(len(endorsed), 1)
        self.assertEqual(len(errored), 1)
        self.assertFalse('wadm_jstaff' in endorsed)
        self.assertTrue('cpnebeng' in endorsed)
