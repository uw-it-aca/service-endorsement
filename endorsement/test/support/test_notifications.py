# Copyright 2023 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.test.support import SupportApiTest


class TestSupportNotifications(SupportApiTest):
    @property
    def reverse_id(self):
        return 'endorsee_notifications'

    def test_statistics(self):
        self._test_good_page()

    def test_bogus_user_statistics(self):
        self._test_invalid_user()
