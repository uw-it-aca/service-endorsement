# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.services import endorsement_services


class TestEndorsementEndorseeAPI(EndorsementApiTest):
    def test_no_endorsees(self):
        self.set_user('jstaff')
        url = reverse('endorsee_api', kwargs={'endorsee': 'endorsee7'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['endorsements']), 0)

    def test_endorsees(self):
        endorser = get_endorser_model('jfaculty')
        endorsee = get_endorsee_model('endorsee7')

        endorsement_count = 0
        for service in endorsement_services():
            endorsement_count += 1
            service.store_endorsement(endorser, endorsee, None, "foobar")

        self.set_user('jstaff')
        url = reverse('endorsee_api', kwargs={'endorsee': 'endorsee7'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['endorsements']), endorsement_count)
        endorsements = {e['category_code']: e for e in data['endorsements']}
        for service in endorsement_services():
            self.assertTrue(service.category_code in endorsements)
            e = endorsements[service.category_code]
            self.assertEqual(e['reason'], 'foobar')
            self.assertEqual(e['endorser']['netid'], 'jfaculty')
            self.assertEqual(e['endorsee']['netid'], 'endorsee7')

    def test_bogus_user_endorsees(self):
        self.set_user('jstudent')
        self.request.session['samlUserdata'] = {
            'uwnetid': ['jstudent'],
            'affiliations': ['student'],
            'eppn': ['jstudent@washington.edu'],
            'scopedAffiliations': [],
            'isMemberOf': ['u_test_group', 'u_test_another_group'],
        }.copy()
        self.request.session.save()
        url = reverse('endorsee_api', kwargs={'endorsee': 'endorsee7'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)
