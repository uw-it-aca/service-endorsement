from django.test.utils import override_settings
from django.test import TestCase
from endorsement.services import endorsement_services


@override_settings(ENDORSEMENT_SERVICES='bogus')
class TestServiceBase(TestCase):
    def xtest_bogus_services_setting(self):
        with self.assertRaises(Exception):
            import pdb; pdb.set_trace()
            endorsement_services()
