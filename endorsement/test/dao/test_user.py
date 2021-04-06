# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from django.test import TransactionTestCase
from endorsement.exceptions import UnrecognizedUWNetid
from endorsement.models.core import Endorser, Endorsee
from endorsement.dao.user import (
    get_endorser_model, get_endorsee_model,
    get_endorsee_email_model, is_shared_netid)


class TestUserDao(TransactionTestCase):

    def test_get_endorser_model(self):
        user = get_endorser_model('jstaff')
        self.assertIsNotNone(user)
        self.assertEqual(user.regid,
                         '10000000000000000000000000000001')
        self.assertTrue(user.is_valid)

        qset = Endorser.objects.filter(netid='jstaff')
        self.assertEqual(len(qset), 1)

        self.assertIsNotNone(Endorser.objects.get(netid='jstaff'))

    def test_get_endorsee_model(self):
        user = get_endorsee_model('endorsee2')
        self.assertIsNotNone(user)
        self.assertEqual(user.display_name, "SIMON ENDORSEE2")
        self.assertTrue(user.kerberos_active_permitted)

        qset = Endorsee.objects.filter(netid='endorsee2')
        self.assertEqual(len(qset), 1)

        self.assertIsNotNone(Endorsee.objects.get(netid='endorsee2'))

        self.assertRaises(UnrecognizedUWNetid,
                          get_endorsee_model,
                          'endorsee5')
        qset = Endorsee.objects.filter(netid='endorsee5')
        self.assertEqual(len(qset), 0)

    def test_get_endorsee_email_model(self):
        endorser = get_endorser_model('jstaff')
        endorsee = get_endorsee_model('endorsee2')
        email = get_endorsee_email_model(endorsee, endorser)
        self.assertEqual(email.email, "endorsee2@uw.edu")

    def test_shared_netids(self):
        self.assertTrue(is_shared_netid('endorsee3'))
        self.assertTrue(is_shared_netid('endorsee7'))
