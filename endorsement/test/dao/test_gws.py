# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from endorsement.dao.gws import is_group_member
from endorsement.test.dao import TestDao


class TestGwsDao(TestDao):

    def test_is_group_member(self):
        group = 'uw_employee'

        self.assertTrue(is_group_member('jstaff', group))
        self.assertTrue(is_group_member('jfaculty', group))

        self.assertFalse(is_group_member("notareal_uwnetid", group))
        self.assertFalse(is_group_member("nomockid", group))

        # test exception
        self.assertRaises(Exception,
                          is_group_member,
                          None)
