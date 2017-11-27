from django.test import TestCase
from uw_gws.utilities import fdao_gws_override
from uw_pws.util import fdao_pws_override
from uw_uwnetid.util import fdao_uwnetid_override


@fdao_gws_override
@fdao_pws_override
@fdao_uwnetid_override
class TestDao(TestCase):

    def setUp(self):
        pass
