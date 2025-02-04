# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta


class NotificationsTestCase(TestCase):
    def days_ago(self, days):
        return self.now - timedelta(days=days)

    def message_timing(self, results):
        offsets = [
            ('one',            self.policy.days_till_expiration(1)),
            ('one + 1 day',    self.policy.days_till_expiration(1) - 1),
            ('two - 1 day',    self.policy.days_till_expiration(2) + 1),
            ('two',            self.policy.days_till_expiration(2)),
            ('two + 1 day',    self.policy.days_till_expiration(2) - 1),
            ('three - 1 day',  self.policy.days_till_expiration(3) + 1),
            ('three',          self.policy.days_till_expiration(3)),
            ('three + 1 day',  self.policy.days_till_expiration(3) - 1),
            ('four - 1 day',   self.policy.days_till_expiration(4) + 1),
            ('four',           self.policy.days_till_expiration(4)),
            ('four + 1 day',   self.policy.days_till_expiration(4) - 1),
            ('four + 2 days',  self.policy.days_till_expiration(4) - 2),
            ('grace - 1 day',  self.policy.graceperiod - 1),
            ('grace',         -(self.policy.graceperiod)),
            ('grace + 1 day', -(self.policy.graceperiod + 1))]

        self.assertEqual(len(offsets), len(results))

        for i, offset in enumerate(offsets):
            self.notice_and_expire(offset, results[i])

    def notice_and_expire(self, offset, expected):
        test_date = self.now - timedelta(days=offset[1])
        days = self.policy.lifetime - offset[1]

        models = self.policy.records_to_expire_on_date(test_date)
        self.assertEqual(
            models.count(), expected[0],
            f"{abs(offset[1])} days after expiration (level {offset[0]})")
        models.update(datetime_expired=test_date, is_deleted=True)

        for level in range(1, 5):
            models = self.policy.records_to_warn_on_date(test_date, level)
            self.assertEqual(
                models.count(), expected[level],
                (f"warning_{level} mismatch: {offset[1]} days before "
                 f"expiration (warning level: {offset[0]})"))
            models.update(**{f"datetime_notice_{level}_emailed": test_date})
