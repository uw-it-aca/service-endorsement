import json
from django.urls import reverse
from endorsement.models import EndorsementRecord
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import store_endorsement
from endorsement.test.api import EndorsementApiTest
from endorsement.services import get_endorsement_service


class TestEndorsementSharedNetidsAPI(EndorsementApiTest):
    def test_shared_netids(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('wadm_jstaff')

        self.assertEqual(len(
            EndorsementRecord.objects.get_endorsements_for_endorser(
                endorser)), 0)

        service = get_endorsement_service('canvas')
        store_endorsement(
            endorser, endorsee, service.category_code,
            service.subscription_codes, None, "for fun")

        self.set_user('jstaff')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)

        self.assertTrue(data['endorser']['netid'] == 'jstaff')
        self.assertEqual(len(data['shared']), 12)

        netids = {v['netid']: i for i, v in enumerate(data['shared'])}

        if (get_endorsement_service('o365') or
                get_endorsement_service('google') or
                get_endorsement_service('canvas')):
            self.assertTrue('cpnebeng' in netids)
            self.assertTrue('wadm_jstaff' in netids)

        endorsed = 0
        for u in data['shared']:
            for e, v in u['endorsements'].items():
                if 'datetime_endorsed' in v:
                    endorsed += 1

        self.assertEquals(endorsed, 1)

        # test o365 and g suite for cat 22
        if get_endorsement_service('o365'):
            self.assertTrue('nebionotic' not in netids)

        if get_endorsement_service('google'):
            self.assertTrue('nebionotic' not in netids)

        # test canvas administrator
        if get_endorsement_service('canvas'):
            self.assertTrue(
                'canvas' not in data['shared'][netids[
                    'cpnebeng']]['endorsements'])
            self.assertTrue(
                'canvas' in data['shared'][netids[
                    'wadm_jstaff']]['endorsements'])

    def test_invalid_shared_netids(self):
        self.set_user('endorsee7')
        url = reverse('shared_api')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)
