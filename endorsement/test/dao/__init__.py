from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings


FDAO = 'restclients.dao_implementation.gws.File'
FDAO_PWS = 'restclients.dao_implementation.pws.File'


dao_test_override = override_settings(
    RESTCLIENTS_GWS_DAO_CLASS=FDAO,
    RESTCLIENTS_PWS_DAO_CLASS=FDAO_PWS)


@dao_test_override
class TestDao(TestCase):

    def setUp(self):
        pass
