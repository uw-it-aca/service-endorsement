import json
from django.urls import reverse
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.test.api import EndorsementApiTest
from endorsement.services import endorsement_services


class TestEndorsementEndorseAPI(EndorsementApiTest):
    reset_sequences = True

    def test_service_endorse_all(self):

        self.set_user('jstaff')
        url = reverse('endorse_api')

        seen = []
        for service in endorsement_services():
            seen.append(service.service_name)

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
                for s in [s.service_name for s in endorsement_services()]:
                    v[s] = {
                        "state": True,
                        "reason": "Student mentoring"
                    } if s == service.service_name else {
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
                for s in endorsement_services():
                    self.assertTrue(s.service_name in v['endorsements'])
                    endorsement = v['endorsements'][s.service_name]
                    if (endorsement['endorsee']['is_person']
                            or s.supports_shared_netids):
                        if s.service_name == service.service_name:
                            if 'error' in endorsement:
                                self.assertFalse(
                                    s.valid_endorsee(
                                        get_endorsee_model(
                                            endorsement['endorsee']['netid']),
                                        get_endorser_model('jstaff')))
                            else:
                                self.assertEqual(
                                    endorsement['category_code'],
                                    service.category_code)
                                self.assertEqual(
                                    endorsement['endorsee']['netid'],
                                    endorsee)
                                self.assertEqual(
                                    endorsement['endorser']['netid'], 'jstaff')
                        elif s.service_name not in seen:
                            if 'error' in endorsement:
                                self.assertFalse(
                                    s.valid_endorsee(
                                        get_endorsee_model(
                                            endorsement['endorsee']['netid']),
                                        get_endorser_model('jstaff')))
                            else:
                                self.assertFalse(endorsement['endorsed'])
                    else:
                        self.assertTrue('error' in endorsement)
