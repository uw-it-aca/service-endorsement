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
