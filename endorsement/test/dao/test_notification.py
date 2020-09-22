from django.test import TransactionTestCase
from django.core import mail
from endorsement.services import ENDORSEMENT_SERVICES, service_name_list
from endorsement.dao.notification import (
    notify_endorsees, notify_endorsers,
    get_unendorsed_unnotified, get_endorsed_unnotified,
    notify_invalid_endorser)
from endorsement.dao.endorse import get_endorsements_by_endorser
from endorsement.dao.user import get_endorser_model, get_endorsee_model
import random


class TestNotificationDao(TransactionTestCase):
    def test_endorsee_notification_message_single(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        svc_key = random.choice(list(ENDORSEMENT_SERVICES.keys()))
        svc = ENDORSEMENT_SERVICES[svc_key]
        svc['initiate'](endorser, endorsee, 'because')
        service_name = svc['category_name']

        endorsements = get_unendorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsees()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Action Required: Your new access to {}'.format(service_name))
        self.assertTrue(service_name in mail.outbox[0].body)
        self.assertTrue('Appropriate Use' in mail.outbox[0].alternatives[0][0])

    def test_endorsee_notification_message_all(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        service_list = service_name_list()
        for service_tag, svc in ENDORSEMENT_SERVICES.items():
            svc['initiate'](endorser, endorsee, 'because')

        endorsements = get_unendorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsees()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Action Required: Your new access to {}'.format(service_list))
        self.assertTrue(service_list in mail.outbox[0].body)
        self.assertTrue('Appropriate Use' in mail.outbox[0].alternatives[0][0])

    def test_endorser_notification_message_single(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        svc_key = random.choice(list(ENDORSEMENT_SERVICES.keys()))
        svc = ENDORSEMENT_SERVICES[svc_key]
        svc['store'](endorser, endorsee, None, 'because')
        service_name = svc['category_name']

        endorsements = get_endorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsers()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Shared NetID access to {}'.format(service_name))
        self.assertTrue(service_name in mail.outbox[0].body)
        self.assertTrue('Shared UW NetID use of these services is bound'
                        in mail.outbox[0].alternatives[0][0])

    def test_endorser_notification_message_all(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        service_list = service_name_list()
        for service_tag, svc in ENDORSEMENT_SERVICES.items():
            svc['store'](endorser, endorsee, None, 'because')

        endorsements = get_endorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsers()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Shared NetID access to {}'.format(service_list))
        self.assertTrue(service_list in mail.outbox[0].body)
        self.assertTrue('Shared UW NetID use of these services is bound'
                        in mail.outbox[0].alternatives[0][0])

    def test_invalid_endorser_notification_message_single(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        svc_key = random.choice(list(ENDORSEMENT_SERVICES.keys()))
        svc = ENDORSEMENT_SERVICES[svc_key]
        svc['store'](endorser, endorsee, None, 'because')
        service_name = svc['category_name']

        endorsements = get_endorsements_by_endorser(endorser)

        self.assertEqual(len(endorsements), 1)

        notify_invalid_endorser(endorser, endorsements)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject[:46],
            'Action Required: Services that you provisioned')
        self.assertTrue(service_name in mail.outbox[0].body)
        self.assertTrue(service_name in mail.outbox[0].alternatives[0][0])
