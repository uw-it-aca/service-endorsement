# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from endorsement.test import (
    fdao_gws_override, fdao_pws_override, fdao_uwnetid_override)


@fdao_gws_override
@fdao_pws_override
@fdao_uwnetid_override
class TestDao(TestCase):

    def setUp(self):
        pass
