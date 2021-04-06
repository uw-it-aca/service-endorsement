# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.test import TransactionTestCase
from django.core import mail
from endorsement.services import endorsement_services, service_names
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

        service = random.choice(endorsement_services())
        service.initiate_endorsement(endorser, endorsee, 'because')
        service_name = service.category_name
        service_link = service.service_link

        endorsements = get_unendorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsees()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Action Required: Your new access to {}'.format(service_name))
        self.assertTrue(service_name in mail.outbox[0].body)
        self.assertTrue(service_link in mail.outbox[0].body)
        self.assertTrue('Appropriate Use' in mail.outbox[0].alternatives[0][0])

    def test_endorsee_notification_message_all(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        service_list = service_names()
        for service in endorsement_services():
            service.initiate_endorsement(endorser, endorsee, 'because')

        endorsements = get_unendorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsees()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Action Required: Your new access to {}'.format(service_list))
        self.assertTrue(service_list in mail.outbox[0].body)

        for service in endorsement_services():
            self.assertTrue(service.service_link in mail.outbox[0].body)

        self.assertTrue('Appropriate Use' in mail.outbox[0].alternatives[0][0])

    def test_endorser_notification_message_single(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        service = random.choice(endorsement_services())
        service.store_endorsement(endorser, endorsee, None, 'because')
        service_name = service.category_name
        service_link = service.service_link

        endorsements = get_endorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsers()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Shared NetID access to {}'.format(service_name))
        self.assertTrue(service_name in mail.outbox[0].body)
        self.assertTrue(service_link in mail.outbox[0].body)
        self.assertTrue('Shared UW NetID use of these services is bound'
                        in mail.outbox[0].alternatives[0][0])

    def test_endorser_notification_message_all(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        service_list = service_names()
        for service in endorsement_services():
            service.store_endorsement(endorser, endorsee, None, 'because')

        endorsements = get_endorsed_unnotified()
        self.assertEqual(len(endorsements), 1)

        notify_endorsers()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Shared NetID access to {}'.format(service_list))
        self.assertTrue(service_list in mail.outbox[0].body)
        for service in endorsement_services():
            self.assertTrue(service.service_link in mail.outbox[0].body)

        self.assertTrue('Shared UW NetID use of these services is bound'
                        in mail.outbox[0].alternatives[0][0])

    def test_invalid_endorser_notification_message_single(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee7')

        service = random.choice(endorsement_services())
        service.store_endorsement(endorser, endorsee, None, 'because')

        endorsements = get_endorsements_by_endorser(endorser)

        self.assertEqual(len(endorsements), 1)

        notify_invalid_endorser(endorser, endorsements)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject[:46],
            'Action Required: Services that you provisioned')
        self.assertTrue(
            service.category_name in mail.outbox[0].body)
        self.assertTrue(
            service.category_name in mail.outbox[0].alternatives[0][0])
