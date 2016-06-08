from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings


FGWS = 'restclients.dao_implementation.gws.File'
FPWS = 'restclients.dao_implementation.pws.File'
FNET = 'restclients.dao_implementation.uwnetid.File'


dao_test_override = override_settings(
    RESTCLIENTS_GWS_DAO_CLASS=FGWS,
    RESTCLIENTS_UWNETID_DAO_CLASS=FNET,
    RESTCLIENTS_PWS_DAO_CLASS=FPWS)


@dao_test_override
class TestDao(TestCase):

    def setUp(self):
        pass
