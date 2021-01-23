import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.services import ENDORSEMENT_SERVICES
from endorsement.dao.user import get_endorser_model, get_endorsee_model
import random


class TestEndorsementEndorsedAPI(EndorsementApiTest):
    def test_no_endorsed(self):
        self.set_user('jfaculty')
        url = reverse('endorsed_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['endorsed']), 0)

    def test_endorsed(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        # test udpate
        svc_key = random.choice(list(ENDORSEMENT_SERVICES.keys()))
        svc = ENDORSEMENT_SERVICES[svc_key]
        svc['store'](endorser, endorsee, None, 'because')

        self.set_user('jstaff')
        url = reverse('endorsed_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('endorsee7' in data['endorsed'])
        for s, v in ENDORSEMENT_SERVICES.items():
            self.assertTrue(s in data['endorsed']['endorsee7']['endorsements'])
            if s == svc_key:
                self.assertTrue(data['endorsed']['endorsee7'][
                    'endorsements'][s]['category_code'], v['category_code'])
