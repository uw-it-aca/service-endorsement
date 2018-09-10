from endorsement.dao import display_datetime
from endorsement.test.dao import TestDao
from datetime import datetime


class TestCommonFunctions(TestDao):

    def test_display_datetime(self):
        d = datetime(1993, 12, 10, 11, 30, 30)
        dd = display_datetime(d)
        self.assertEqual(dd, 'December 10 at 11:30 AM UTC')