from django.urls import reverse
from endorsement.test.api import EndorsementApiTest


class SupportApiTest(EndorsementApiTest):
    @property
    def reverse_id(self):
        return None

    def _test_good_page(self):
        self.set_user('jstaff')
        url = reverse(self.reverse_id)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        
    def _test_invalid_user(self):
        self.set_user('jstudent')
        self.request.session['samlUserdata'] = {
            'uwnetid': ['jstudent'],
            'affiliations': ['student'],
            'eppn': ['jstudent@washington.edu'],
            'scopedAffiliations': [],
            'isMemberOf': ['u_test_group', 'u_test_another_group'],
        }.copy()
        self.request.session.save()
        url = reverse(self.reverse_id)
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)
