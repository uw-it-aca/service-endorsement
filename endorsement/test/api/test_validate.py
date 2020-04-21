import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.exceptions import NoEndorsementException
from endorsement.dao.endorse import (
    store_google_endorsement, clear_office365_endorsement)


class TestEndorsementValidateAPI(EndorsementApiTest):
    def test_validate(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')
        store_google_endorsement(endorser, endorsee, None, 'because')

        try:
            clear_office365_endorsement(endorser, endorsee)
        except NoEndorsementException as ex:
            pass

        self.set_user('jfaculty')

        url = reverse('validate_api')
        data = json.dumps({
            "netids": [
                "endorsee7"
            ]
        })

        response = self.client.post(url, data, content_type='application/json')
        self.assertEquals(response.status_code, 200)

        data = json.loads(response.content)

        self.assertEqual(len(data['validated']), 1)
        self.assertTrue('google' in data['validated'][0]['endorsements'])
        self.assertTrue(data['validated'][0]['netid'], 'endorsee7')
        self.assertTrue(data['validated'][0]['endorsements'][
            'google']['active'])
        self.assertEqual(len(data['validated'][0]['endorsements'][
            'google']['endorsers']), 1)
        self.assertEqual(
            data['validated'][0]['endorsements'][
                'google']['endorsers'][0]['netid'], 'jstaff')

        self.assertTrue('o365' in data['validated'][0]['endorsements'])
        self.assertFalse(data['validated'][0]['endorsements'][
            'o365']['active'])
        self.assertEqual(len(data['validated'][0]['endorsements'][
            'o365']['endorsers']), 0)
