# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.test.services import ServicesApiTest
from endorsement.services import get_endorsement_service


class TestGoogleService(ServicesApiTest):
    @property
    def service(self):
        return get_endorsement_service('google')

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
        endorsee_pre = get_endorsee_model('cpnebeng')

        self.assertEqual(len(
            EndorsementRecord.objects.get_endorsements_for_endorser(
                endorser)), 0)

        self.service.store_endorsement(
            endorser, endorsee, None, "testing")
        self.service.store_endorsement(
            endorser, endorsee_pre, None, "pre-existing")

        self.set_user('jstaff')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data['endorser']['netid'] == 'jstaff')

        endorsible, endorsed = self.get_shared(data)
        self.assertEquals(len(endorsible), 3)

        self.assertTrue('cpnebeng' not in endorsible)
        self.assertTrue('wadm_jstaff' in endorsible)
        # exclude category 22
        self.assertFalse('nebionotic' in endorsible)

    def test_legacy_shared_netid(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('wadm_jstaff')
        cpnebeng = get_endorsee_model('cpnebeng')
        pppmsrv = get_endorsee_model('pppmsrv')

        self.assertEqual(len(
            EndorsementRecord.objects.get_endorsements_for_endorser(
                endorser)), 0)

        self.service.store_endorsement(
            endorser, endorsee, None, "testing")
        self.service.store_endorsement(
            endorser, cpnebeng, None, "pre-existing")
        self.service.store_endorsement(
            endorser, pppmsrv, None, "cat excluded pre-existing")

        # remove pre-existing non-admin
        self.service.clear_endorsement(endorser, cpnebeng)
        # remove pre-existing cat22 non-admin
        self.service.clear_endorsement(endorser, pppmsrv)

        self.set_user('jstaff')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)

        endorsible, endorsed = self.get_shared(data)

        self.assertEquals(len(endorsible), 3)
        self.assertEquals(len(endorsed), 1)
        self.assertTrue(cpnebeng.netid not in endorsible)
        self.assertTrue(pppmsrv.netid not in endorsible)

    def test_endorse_netid(self):
        self._test_endorse_netid()

    def test_endorse_shared(self):
        endorsible, endorsing, endorsed, errored = self._test_endorse({
            "endorsees": {
                # shared resource of administrator type
                "wadm_jstaff": {
                    "name": "ADMIN NETID JSTAFF",
                    "email": "wadm_jstaff@uw.edu",
                    'store': True,
                    self.service.service_name: {
                        "state": True,
                        "reason": "testing"
                    }
                },
                # shared resource of shared type
                "cpnebeng": {
                    "name": "cpneb eng",
                    "email": "cpnebeng@uw.edu",
                    'store': True,
                    self.service.service_name: {
                        "state": True,
                        "reason": "testing"
                    }
                },
            }
        })

        self.assertEqual(len(endorsing), 0)
        self.assertTrue('wadm_jstaff' in endorsed)
        self.assertEqual(len(endorsible), 1)
        self.assertEqual(len(endorsed), 1)
        self.assertEqual(len(errored), 1)
        self.assertFalse('cpnebeng' in endorsed)

    def test_legacy_netid_endorse(self):
        endorser = get_endorser_model('jstaff')
        endorsee_pre = get_endorsee_model('cpnebeng')
        self.service.store_endorsement(
            endorser, endorsee_pre, None, "pre-existing")

        endorsible, endorsing, endorsed, errored = self._test_endorse({
            "endorsees": {
                # endorse invalid, but pre-existing shared
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
        self.assertEqual(len(errored), 1)
        self.assertTrue('cpnebeng' not in endorsed)
