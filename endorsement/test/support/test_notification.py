import json
from django.urls import reverse
from endorsement.test.support import SupportApiTest


class TestSupportNotificationAPI(SupportApiTest):
    def test_search_api(self):
        self.set_user('jstaff')
        url = reverse('notification_api')
        notification_data = {
            'notification': 'warning_1',
            'endorsees': {
                'endorsee1': ['o365'],
                'endorsee2': [],
                'endorsee3': []
            }
        }
        response = self.client.post(
            url, json.dumps(notification_data),
            content_type='application/json')
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        keys = data.keys()
        self.assertTrue('subject' in keys)
        self.assertTrue('text' in keys)
        self.assertTrue('html' in keys)
