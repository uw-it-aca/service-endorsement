import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest


class TestEndorsementSharedNetidsAPI(EndorsementApiTest):
    def test_shared_netids(self):
        self.set_user('jfaculty')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['endorser']['netid'], 'jfaculty')
        self.assertEqual(len(data['shared']), 4)

        netids = []
        for shared in data['shared']:
            netids.append(shared['netid'])

        self.assertTrue('endorsee3' in netids)
        self.assertTrue('nebionotic' in netids)
        self.assertFalse('emailinfo' in netids)

    def test_invalid_shared_netids(self):
        self.set_user('endorsee7')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)
