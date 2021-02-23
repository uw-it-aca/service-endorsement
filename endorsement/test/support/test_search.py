import json
from django.urls import reverse
from endorsement.test.support import SupportApiTest
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.services import endorsement_services


class TestSupportSearchAPI(SupportApiTest):
    def test_search_api(self):
        endorser = get_endorser_model('jstaff')
        endorsee1 = get_endorsee_model('endorsee2')

        endorsements = 0
        for service in endorsement_services():
            endorsements += 1
            service.store_endorsement(endorser, endorsee1, None, "test")

        self.set_user('jstaff')
        url = reverse('endorsee_api', args=['endorsee2'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(len(data['endorsements']), endorsements)

    def test_bogus_user_search_api(self):
        self.set_user('jstudent')
        self.request.session['samlUserdata'] = {
            'uwnetid': ['jstudent'],
            'affiliations': ['student'],
            'eppn': ['jstudent@washington.edu'],
            'scopedAffiliations': [],
            'isMemberOf': ['u_test_group', 'u_test_another_group'],
        }.copy()
        self.request.session.save()
        url = reverse('endorsee_api', args=['endorsee2'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)
