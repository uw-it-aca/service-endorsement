# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from django.utils import timezone
from django.core import mail
from endorsement.models import Accessor, Accessee, AccessRight, AccessRecord
from endorsement.util.string import listed_list
from endorsement.dao.notification import notify_accessors
from endorsement.services import endorsement_services
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

        service_names = []
        for service in endorsement_services():
            if service.valid_person_endorsee(endorsee):
                service.initiate_endorsement(endorser, endorsee, 'because')
                service_names.append(service.category_name)

        service_list = listed_list(service_names)

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

        service_names = []
        for service in endorsement_services():
            if service.valid_person_endorsee(endorsee):
                service.store_endorsement(endorser, endorsee, None, 'because')
                service_names.append(service.category_name)

        service_list = listed_list(service_names)

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

        notify_invalid_endorser(endorsements)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject[:46],
            'Action Required: Services that you provisioned')
        self.assertTrue(
            service.category_name in mail.outbox[0].body)
        self.assertTrue(
            service.category_name in mail.outbox[0].alternatives[0][0])


class TestAccessorNotification(TransactionTestCase):
    def setUp(self):
        now = timezone.now()
        self.accessee = Accessee.objects.create(
            netid='accessee', display_name="Netid Accessee",
            regid='AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', is_valid=True)
        self.accessor = Accessor.objects.create(
            name='accessor', display_name='Netid Accessor',
            is_valid=True, is_shared_netid=False, is_group=False)
        self.accessor2 = Accessor.objects.create(
            name='accessor2', display_name='Netid Accessor Two',
            is_valid=True, is_shared_netid=False, is_group=False)
        self.group_accessor = Accessor.objects.create(
            name='endorsement_group', display_name='Group Accessor',
            is_valid=True, is_shared_netid=False, is_group=True)

        aaaott = AccessRight.objects.create(
            name='1', display_name='AllAccessAllOfTheTime')
        sasott = AccessRight.objects.create(
            name='2', display_name='SomeAccessSomeOfTheTime')

        AccessRecord.objects.create(
            accessee=self.accessee, accessor=self.accessor,
            access_right=aaaott, datetime_granted=now)
        AccessRecord.objects.create(
            accessee=self.accessee, accessor=self.group_accessor,
            access_right=sasott, datetime_granted=now)
        AccessRecord.objects.create(
            accessee=self.accessee, accessor=self.accessor2,
            access_right=sasott, datetime_granted=now, is_reconcile=True)

    def test_access_notifications(self):
        notify_accessors()
        self.assertEqual(len(mail.outbox), 2)

        self.assertEqual(len(mail.outbox[0].to), 1)
        self.assertEqual(len(mail.outbox[1].to), 2)
        self.assertTrue('AllAccessAllOfTheTime' in mail.outbox[0].body)
        self.assertTrue('SomeAccessSomeOfTheTime' in mail.outbox[1].body)
