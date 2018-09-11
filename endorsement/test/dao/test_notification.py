from django.test import TransactionTestCase
from endorsement.dao.notification import (
    get_unendorsed_unnotified, create_endorsee_message,
    get_endorsed_unnotified, create_endorser_message)
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import (
    store_office365_endorsement, store_google_endorsement,
    initiate_office365_endorsement, initiate_google_endorsement)


class TestNotificationDao(TransactionTestCase):
    def test_endorsee_notification_message(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        initiate_office365_endorsement(endorser, endorsee, 'because')
        initiate_google_endorsement(endorser, endorsee, 'because')

        endorsements = get_unendorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        for email, endorsers in endorsements.items():
            for endorser_netid, endorsers in endorsers['endorsers'].items():
                msg = create_endorsee_message(endorsers)
                self.assertEqual(
                    msg[0], 'Your new access to UW Microsoft and Google tools')

    def test_endorser_notification_message(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        store_office365_endorsement(endorser, endorsee, None, 'because')
        store_google_endorsement(endorser, endorsee, None, 'because')

        endorsements = get_endorsed_unnotified()
        for email, endorsed in endorsements.items():
            (subject, text_body, html_body) = create_endorser_message(endorsed)
            self.assertEqual(
                subject, 'Shared NetID access to UW Office 365 and UW G Suite')
            self.assertTrue(len(text_body) > 0)
            self.assertTrue(len(html_body) > 0)
