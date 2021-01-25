import json
from django.urls import reverse
from endorsement.test.api import EndorsementApiTest


class TestEndorsementSharedNetidsAPI(EndorsementApiTest):
    def test_shared_netids(self):
        self.set_user('jstaff')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data['endorser']['netid'] == 'jstaff')
        self.assertEqual(len(data['shared']), 14)

        netids = {v['netid']: i for i, v in enumerate(data['shared'])}

        self.assertTrue('cpnebeng' in netids)
        self.assertTrue('wadm_jstaff' in netids)

        # test o365 and g suite for cat 22
        self.assertTrue('nebionotic' not in netids)

        # test canvas administrator
        self.assertTrue(
            'canvas' not in data['shared'][netids['cpnebeng']]['endorsements'])
        self.assertTrue(
            'canvas' in data['shared'][netids['wadm_jstaff']]['endorsements'])


    def test_invalid_shared_netids(self):
        self.set_user('endorsee7')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)
