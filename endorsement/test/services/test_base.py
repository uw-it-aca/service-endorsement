# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test.utils import override_settings
from django.test import TestCase
from endorsement.services import _load_endorsement_services, is_valid_endorser


class TestServiceBase(TestCase):
    @override_settings(ENDORSEMENT_SERVICES='bogus')
    def test_bogus_services_setting(self):
        with self.assertRaises(Exception):
            _load_endorsement_services()

    def test_valid_endorser(self):
        self.assertTrue(is_valid_endorser('jstaff'))
        self.assertTrue(is_valid_endorser('jfaculty'))

        self.assertFalse(is_valid_endorser('notareal_uwnetid'))
        self.assertFalse(is_valid_endorser('nomockid'))

        # test exception
        self.assertFalse(is_valid_endorser(None))
