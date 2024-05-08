# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta


class NotificationsTestCase(TestCase):
    def days_ago(self, days):
        return self.now - timedelta(days=days)

    def notice_and_expire_test(self, expirer, warner, offset, expected):
        test_date = self.now - timedelta(days=offset[1])
        days = self.lifetime - offset[1]

        models = expirer(test_date)
        self.assertEqual(
            models.count(), expected[0],
            f"test expired at offset level {offset[0]} (day {days})")
        models.update(datetime_expired=test_date, is_deleted=True)

        for level in range(1, 5):
            models = warner(test_date, level)
            self.assertEqual(
                models.count(), expected[level],
                (f"level {level} test at offset "
                 f"{offset[0]} days ago (day {days})"))
            models.update(**{f"datetime_notice_{level}_emailed": test_date})

    def message_timing(self, warning_level, results):
        offsets = [
            ('one',            warning_level(1)),
            ('one + 1 day',    warning_level(1) - 1),
            ('two - 1 day',    warning_level(2) + 1),
            ('two',            warning_level(2)),
            ('two + 1 day',    warning_level(2) - 1),
            ('three - 1 day',  warning_level(3) + 1),
            ('three',          warning_level(3)),
            ('three + 1 day',  warning_level(3) - 1),
            ('four - 1 day',   warning_level(4) + 1),
            ('four',           warning_level(4)),
            ('four + 1 day',   warning_level(4) - 1),
            ('four + 2 days',  warning_level(4) - 2),
            ('grace - 1 day', -(self.graceperiod - 1)),
            ('grace',         -(self.graceperiod)),
            ('grace + 1 day', -(self.graceperiod + 1))]

        self.assertEqual(len(offsets), len(results))

        for i, offset in enumerate(offsets):
            self.notice_and_expire(offset, results[i])
