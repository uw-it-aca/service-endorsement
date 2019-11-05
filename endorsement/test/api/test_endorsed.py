import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import (
    store_office365_endorsement)


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

        store_office365_endorsement(endorser, endorsee, None, 'because')

        self.set_user('jstaff')
        url = reverse('endorsed_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('endorsee7' in data['endorsed'])
        self.assertTrue('o365' in data['endorsed']['endorsee7'][
            'endorsements'])
        self.assertTrue('google' in data['endorsed']['endorsee7'][
            'endorsements'])
        self.assertTrue(data['endorsed']['endorsee7']['endorsements'][
            'o365']['category_code'], 235)
