import json
from django.core.urlresolvers import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.exceptions import NoEndorsementException
from endorsement.dao.endorse import (
    clear_office365_endorsement)


class TestEndorsementEndorseAPI(EndorsementApiTest):
    def test_endorse(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')
        try:
            clear_office365_endorsement(endorser, endorsee)
        except NoEndorsementException as ex:
            pass

        self.set_user('jstaff')
        url = reverse('endorse_api')

        data = json.dumps({
            "endorsee7": {
                "name": "JERRY ENDORSEE7",
                "email": "endorsee7@uw.edu",
                "reason": "Student mentoring",
                "google": True
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
        self.assertFalse('o365' in data['endorsed']['endorsee7'])
