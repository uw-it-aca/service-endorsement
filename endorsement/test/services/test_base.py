from django.test.utils import override_settings
from django.test import TestCase
from endorsement.services import endorsement_services


class TestServiceBase(TestCase):
    @override_settings(ENDORSEMENT_SERVICES='bogus')
    def test_bogus_services_setting(self):
        with self.assertRaises(Exception):
            endorsement_services()