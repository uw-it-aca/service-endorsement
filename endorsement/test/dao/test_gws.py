# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0
from endorsement.dao.gws import is_valid_endorser, endorser_group_member
from endorsement.test.dao import TestDao


class TestGwsDao(TestDao):

    def test_is_valid_endorser(self):
        self.assertTrue(is_valid_endorser('jstaff'))
        self.assertTrue(is_valid_endorser('jfaculty'))

        self.assertFalse(is_valid_endorser("notareal_uwnetid"))
        self.assertFalse(is_valid_endorser("nomockid"))

        # test exception
        self.assertFalse(is_valid_endorser(None))
        self.assertRaises(Exception,
                          endorser_group_member,
                          None)
