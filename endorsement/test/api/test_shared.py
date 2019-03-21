import json
from django.core.urlresolvers import reverse
from endorsement.test.api import EndorsementApiTest


class TestEndorsementSharedNetidsAPI(EndorsementApiTest):
    def test_shared_netids(self):
        self.set_user('jfaculty')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['endorser']['netid'], 'jfaculty')
        self.assertEqual(len(data['shared']), 6)

        netids = []
        for shared in data['shared']:
            netids.append(shared['netid'])

        self.assertTrue('emailinfo' in netids)
        self.assertTrue('endorsee3' in netids)
        self.assertTrue('nebionotic' in netids)

    def test_invalid_shared_netids(self):
        self.set_user('endorsee7')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)
