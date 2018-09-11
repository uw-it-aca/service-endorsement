from django.core.urlresolvers import reverse
from userservice.user import get_original_user
from endorsement.test.views import require_url, TestViewApi
from endorsement.models.core import EndorsementRecord
from endorsement.exceptions import NoEndorsementException
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import (
    clear_office365_endorsement, initiate_office365_endorsement)


@require_url('accept_view', 'endorsement urls not configured',
             kwargs={'accept_id': "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"})
class TestAccept(TestViewApi):
 
    @classmethod
    def setUpTestData(cls):
        endorser = get_endorser_model('jfaculty')
        endorsee = get_endorsee_model('endorsee7')
        try:
            clear_office365_endorsement(endorser, endorsee)
        except NoEndorsementException as ex:
            pass

        initiate_office365_endorsement(endorser, endorsee, 'foobar')

        endorsement = EndorsementRecord.objects.get(endorser=endorser,
                                                    endorsee=endorsee)
        cls.accept_id = endorsement.accept_id

    def test_normal_view(self):
        url = reverse('accept_view',
                      kwargs={"accept_id": self.accept_id})

        request = self.get_request('/', 'endorsee7')
        self.assertEqual(get_original_user(request), 'endorsee7')

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_invalid_viewer(self):
        request = self.get_request('/', 'endorsee6')
        self.assertEqual(get_original_user(request), 'endorsee6')

        url = reverse('accept_view',
                      kwargs={"accept_id": self.accept_id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 401)

    def test_invalid_request(self):
        request = self.get_request('/', 'endorsee6')
        self.assertEqual(get_original_user(request), 'endorsee6')

        url = reverse('accept_view',
                      kwargs={"accept_id": 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)