from django.test.utils import override_settings
from django.urls import reverse
from endorsement.test.support import SupportApiTest
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.services import endorsement_services


class TestSupportStatisticsAPI(SupportApiTest):
    def test_statistics_api(self):
        endorser = get_endorser_model('jstaff')
        endorsee1 = get_endorsee_model('endorsee2')
        endorsee2 = get_endorsee_model('wadm_jstaff')

        for service in endorsement_services():
            service.store_endorsement(endorser, endorsee1, None, "test")
            service.store_endorsement(endorser, endorsee2, None, "test")

        self.set_user('jstaff')
        url = reverse('statistics_api', args=['service'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        url = reverse('statistics_api', args=['shared'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        url = reverse('statistics_api', args=['endorsers'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        url = reverse('statistics_api', args=['reasons'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        url = reverse('statistics_api', args=['rate/90'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_bogus_statistics_url(self):
        self.set_user('jstaff')
        url = reverse('statistics_api', args=['other'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 543)

    def test_bogus_user_statistics_api(self):
        self.set_user('jstudent')
        self.request.session['samlUserdata'] = {
            'uwnetid': ['jstudent'],
            'affiliations': ['student'],
            'eppn': ['jstudent@washington.edu'],
            'scopedAffiliations': [],
            'isMemberOf': ['u_test_group', 'u_test_another_group'],
        }.copy()
        self.request.session.save()
        url = reverse('statistics_api', args=['service'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)
