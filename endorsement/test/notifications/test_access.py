# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TransactionTestCase
from django.utils import timezone
from django.core import mail
from endorsement.models import Accessor, Accessee, AccessRight, AccessRecord
from endorsement.util.string import listed_list
from endorsement.notifications.access import notify_accessors
import random


class TestAccessNotifications(TransactionTestCase):
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
