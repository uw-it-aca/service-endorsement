from endorsement.dao.gws import is_valid_endorser,\
    get_endorser_endorsees
from endorsement.test.dao import TestDao


class TestGwsDao(TestDao):

    def test_is_valid_endorser(self):
        self.assertTrue(is_valid_endorser('jstaff'))
        self.assertTrue(is_valid_endorser('jfaculty'))

        self.assertFalse(is_valid_endorser("notareal_uwnetid"))
        self.assertFalse(is_valid_endorser("nomockid"))

    def test_get_endorsees_by_endorser(self):
        endorse_list = get_endorser_endorsees()
        self.assertEqual(len(endorse_list), 2)

        self.assertEqual(endorse_list[0].get("endorser"), 'jstaff')
        endorsee_list = endorse_list[0].get("endorsees")
        self.assertEqual(len(endorsee_list), 2)
        self.assertEqual(endorsee_list[0], 'endorsee1')
        self.assertEqual(endorsee_list[1], 'endorsee2')

        self.assertEqual(endorse_list[1].get("endorser"), 'jfaculty')
        self.assertEqual(len(endorse_list[1].get("endorsees")), 0)
