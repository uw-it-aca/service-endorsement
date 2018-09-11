from django.test import TestCase
from endorsement.test import (
    fdao_gws_override, fdao_pws_override, fdao_uwnetid_override)


@fdao_gws_override
@fdao_pws_override
@fdao_uwnetid_override
class TestDao(TestCase):

    def setUp(self):
        pass
