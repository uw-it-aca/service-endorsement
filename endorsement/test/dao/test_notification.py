from django.test import TransactionTestCase
from django.core import mail
from endorsement.dao.notification import (
    notify_endorsees, notify_endorsers,
    get_unendorsed_unnotified, get_endorsed_unnotified)
from endorsement.dao.user import get_endorser_model, get_endorsee_model
from endorsement.dao.endorse import (
    store_office365_endorsement, store_google_endorsement,
    initiate_office365_endorsement, initiate_google_endorsement,
    initiate_canvas_endorsement)


class TestNotificationDao(TransactionTestCase):
    def test_endorsee_notification_message(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        initiate_office365_endorsement(endorser, endorsee, 'because')
        initiate_google_endorsement(endorser, endorsee, 'because')
        initiate_canvas_endorsement(endorser, endorsee, 'because')

        endorsements = get_unendorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsees()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Action Required: Your new access to UW Office 365, UW G Suite and UW Canvas')
        self.assertTrue(
            'UW Office 365, UW G Suite and UW Canvas' in mail.outbox[0].body)
        self.assertTrue('Appropriate Use' in mail.outbox[0].alternatives[0][0])

    def test_endorser_notification_message(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        store_office365_endorsement(endorser, endorsee, None, 'because')
        store_google_endorsement(endorser, endorsee, None, 'because')

        endorsements = get_endorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsers()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Shared NetID access to UW Office 365 and UW G Suite')
        self.assertTrue('UW Office 365 and UW G Suite' in mail.outbox[0].body)
        self.assertTrue('Shared UW NetID use of these services is bound'
                        in mail.outbox[0].alternatives[0][0])
