from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from uw_gws.utilities import fdao_gws_override
from uw_pws.util import fdao_pws_override
from uw_uwnetid.util import fdao_uwnetid_override


dao_test_override = override_settings(
    RESTCLIENTS_GWS_DAO_CLASS=fdao_gws_override,
    RESTCLIENTS_UWNETID_DAO_CLASS=fdao_uwnetid_override,
    RESTCLIENTS_PWS_DAO_CLASS=fdao_pws_override)


@dao_test_override
class TestDao(TestCase):

    def setUp(self):
        pass
