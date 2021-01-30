import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest
from endorsement.services import endorsement_services
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
        service = random.choice(endorsement_services())
        service.store_endorsement(endorser, endorsee, None, 'because')

        self.set_user('jstaff')
        url = reverse('endorsed_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue('endorsee7' in data['endorsed'])
        for s in endorsement_services():
            self.assertTrue(s.service_name() in data[
                'endorsed']['endorsee7']['endorsements'])
            if s.service_name() == service.service_name():
                self.assertTrue(data['endorsed']['endorsee7'][
                    'endorsements'][s.service_name()]['category_code'],
                                s.category_code())
