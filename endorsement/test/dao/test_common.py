# Copyright 2026 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import datetime

from endorsement.dao import display_datetime
from endorsement.test.dao import TestDao


class TestCommonFunctions(TestDao):

    def test_display_datetime(self):
        d = datetime.datetime(1993, 12, 10, 11, 30, 30).astimezone(datetime.timezone.utc)
        dd = display_datetime(d)
        self.assertEqual(dd[:23], 'December 10 at 11:30 AM')
