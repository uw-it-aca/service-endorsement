import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.services import ENDORSEMENT_SERVICES


class TestEndorsementEndorseAPI(EndorsementApiTest):
    reset_sequences = True

    def test_service_endorse_all(self):
        services = list(ENDORSEMENT_SERVICES.keys())

        self.set_user('jstaff')
        url = reverse('endorse_api')

        seen = []
        for svc_tag, svc in ENDORSEMENT_SERVICES.items():
            seen.append(svc_tag)

            data = {
                "endorsees": {
                    "endorsee7": {
                        "name": "JERRY ENDORSEE7",
                        "email": "endorsee7@uw.edu",
                    },
                    "endorsee3": {
                        "name": "SHARED NETID ENDORSEE3",
                        "email": "endorsee3@uw.edu",
                    }
                }
            }

            for endorsee, v in data["endorsees"].items():
                for s in services:
                    v[s] = {
                        "state": True,
                        "reason": "Student mentoring"
                    } if s == svc_tag else {
                        "state": False
                    }

            response = self.client.post(
                url, json.dumps(data), content_type='application/json')
            self.assertEquals(response.status_code, 200)
            data = json.loads(response.content)
            self.assertEqual(data['endorser']['netid'], 'jstaff')
            self.assertTrue('endorsee7' in data['endorsed'])
            self.assertTrue('endorsee3' in data['endorsed'])
            for endorsee, v in data["endorsed"].items():
                for s in services:
                    self.assertTrue(s in v['endorsements'])
                    endorsement = v['endorsements'][s]
                    if (endorsement['endorsee']['is_person']
                            or ENDORSEMENT_SERVICES[s]['valid_shared']):
                        if s == svc_tag:
                            self.assertEqual(
                                endorsement['category_code'],
                                svc['category_code'])
                            self.assertEqual(
                                endorsement['endorsee']['netid'],
                                endorsee)
                            self.assertEqual(
                                endorsement['endorser']['netid'], 'jstaff')
                        elif s not in seen:
                            self.assertFalse(endorsement['endorsed'])
                    else:
                        self.assertTrue('error' in endorsement)

