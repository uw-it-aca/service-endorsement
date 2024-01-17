# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest


class TestEndorsementEndorseAPI(EndorsementApiTest):
    def test_invalid_endorser(self):
        self.set_user('javerage')
        url = reverse('endorse_api')

        endorse_data = {
            "endorsees": {
                "endorsee2": {
                    "name": "JERRY ENDORSEE2",
                    "email": "endorsee2@uw.edu",
                    "service": {
                        "state": True,
                        "reason": "testing"
                    }
                }
            }
        }

        response = self.client.post(
            url, json.dumps(endorse_data), content_type='application/json')
        self.assertEquals(response.status_code, 401)

    def test_invalid_endorsee(self):
        self.set_user('jstaff')
        url = reverse('endorse_api')

        endorse_data = {
            "endorsees": {
                "endorsee99": {
                    "name": "Unknown Endorsee99",
                    "email": "uendorsee99@uw.edu",
                    "service": {
                        "state": True,
                        "reason": "testing"
                    }
                }
            }
        }

        response = self.client.post(
            url, json.dumps(endorse_data), content_type='application/json')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('error' in data['endorsed']['endorsee99'])

    def test_invalid_service(self):
        self.set_user('jstaff')
        url = reverse('endorse_api')

        endorse_data = {
            "endorsees": {
                "endorsee2": {
                    "name": "JERRY ENDORSEE2",
                    "email": "endorsee2@uw.edu",
                    "mumble": {
                        "state": True,
                        "reason": "testing"
                    }
                }
            }
        }

        response = self.client.post(
            url, json.dumps(endorse_data), content_type='application/json')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse('mumble' in data['endorsed']['endorsee2'])


class TestEndorsementAdminEndorseAPI(EndorsementApiTest):
    def test_valid_override(self):
        self.set_user('faculty')
        self.set_userservice_override('jstaff')
        url = reverse('endorse_api')

        endorse_data = {
            "endorsees": {
                "endorsee6": {
                    "name": "JERRY ENDORSEE6",
                    "email": "endorsee6@uw.edu",
                    "mumble": {
                        "state": True,
                        "reason": "testing"
                    }
                }
            }
        }

        response = self.client.post(
            url, json.dumps(endorse_data), content_type='application/json')
        self.assertEquals(response.status_code, 200)


class TestEndorsementSupportEndorseAPI(EndorsementApiTest):
    def test_valid_override(self):
        self.set_user('faculty')
        self.request.session['samlUserdata']['isMemberOf'] = [
            'u_test_group', 'u_test_another_group',
            'u_acadev_provision_support']
        self.request.session.save()
        self.set_userservice_override('jstaff')
        url = reverse('endorse_api')

        endorse_data = {
            "endorsees": {
                "endorsee6": {
                    "name": "JERRY ENDORSEE6",
                    "email": "endorsee6@uw.edu",
                    "mumble": {
                        "state": True,
                        "reason": "testing"
                    }
                }
            }
        }

        response = self.client.post(
            url, json.dumps(endorse_data), content_type='application/json')
        self.assertEquals(response.status_code, 401)
