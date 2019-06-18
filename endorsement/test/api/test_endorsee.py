import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import (
    store_office365_endorsement)


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

        store_office365_endorsement(endorser, endorsee, None, 'foobar')

        self.set_user('jstaff')
        url = reverse('endorsee_api', kwargs={'endorsee': 'endorsee7'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['endorsements']), 1)
        self.assertEqual(data['endorsements'][0]['category_code'], 235)
        self.assertEqual(data['endorsements'][0]['reason'], 'foobar')
        self.assertEqual(
            data['endorsements'][0]['endorser']['netid'], 'jfaculty')
        self.assertEqual(
            data['endorsements'][0]['endorsee']['netid'], 'endorsee7')
