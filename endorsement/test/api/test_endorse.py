import json
from django.core.urlresolvers import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.exceptions import NoEndorsementException
from endorsement.dao.endorse import (
    clear_office365_endorsement)


class TestEndorsementEndorseAPI(EndorsementApiTest):
    def test_endorse_google(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        self.set_user('jstaff')
        url = reverse('endorse_api')

        data = json.dumps({
            "endorsee7": {
                "name": "JERRY ENDORSEE7",
                "email": "endorsee7@uw.edu",
                "reason": "Student mentoring",
                "google": True,
                "o365": False
            }
        })

        response = self.client.post(url, data, content_type='application_json')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['endorser']['netid'], 'jstaff')
        self.assertTrue('endorsee7' in data['endorsed'])
        self.assertTrue('google' in data['endorsed']['endorsee7'])
        self.assertEqual(
            data['endorsed']['endorsee7']['google']['category_code'], 234)
        self.assertEqual(
            data['endorsed']['endorsee7']['google']['endorsee']['netid'],
            'endorsee7')
        self.assertEqual(
            data['endorsed']['endorsee7']['google']['endorser']['netid'],
            'jstaff')
        self.assertTrue('o365' in data['endorsed']['endorsee7'])
        self.assertFalse(data['endorsed']['endorsee7']['o365']['endorsed'])

    def test_endorse_o365(self):
        endorser = get_endorser_model('jfaculty')
        endorsee = get_endorsee_model('endorsee7')

        self.set_user('jfaculty')
        url = reverse('endorse_api')

        data = json.dumps({
            "endorsee7": {
                "name": "JERRY ENDORSEE7",
                "email": "endorsee7@uw.edu",
                "reason": "Student mentoring",
                "o365": True,
                "google": False
            }
        })

        response = self.client.post(url, data, content_type='application_json')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['endorser']['netid'], 'jfaculty')
        self.assertTrue('endorsee7' in data['endorsed'])
        self.assertTrue('o365' in data['endorsed']['endorsee7'])
        self.assertEqual(
            data['endorsed']['endorsee7']['o365']['category_code'], 235)
        self.assertEqual(
            data['endorsed']['endorsee7']['o365']['endorsee']['netid'],
            'endorsee7')
        self.assertEqual(
            data['endorsed']['endorsee7']['o365']['endorser']['netid'],
            'jfaculty')
        self.assertTrue('google' in data['endorsed']['endorsee7'])
        self.assertFalse(data['endorsed']['endorsee7']['google']['endorsed'])
