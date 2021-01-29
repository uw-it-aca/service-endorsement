from endorsement.dao.gws import is_valid_endorser, has_canvas_access
from endorsement.test.dao import TestDao


class TestGwsDao(TestDao):

    def test_is_valid_endorser(self):
        self.assertTrue(is_valid_endorser('jstaff'))
        self.assertTrue(is_valid_endorser('jfaculty'))

        self.assertFalse(is_valid_endorser("notareal_uwnetid"))
        self.assertFalse(is_valid_endorser("nomockid"))

    def test_has_canvas_access(self):
        self.assertTrue(has_canvas_access('endorsee6'))
        self.assertFalse(has_canvas_access('endorsee2'))
