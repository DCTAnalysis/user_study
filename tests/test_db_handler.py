import unittest

from db_handler import DbHandler

class DbHandlerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # create a connection to test database
        self.db = DbHandler()
        # default pre-configured user
        self.user_id = "aaa10022-38b0-4a1a-95af-776f35aa2b8f"

    def tearDown(self):
        pass

    def test_get_participant(self):
        participant = self.db.get_participant(self.user_id)
        self.assertNotEqual(participant, None)
        self.assertEqual(participant[1], self.user_id)