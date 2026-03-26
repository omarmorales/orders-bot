import unittest
from bot.sessions import get_session, reset_session

class TestSessions(unittest.TestCase):
    def test_get_session(self):
        phone = "1234567890"
        session = get_session(phone)
        self.assertEqual(session["state"], "start")
        self.assertEqual(session["order"], [])
        self.assertEqual(session["name"], "")
        self.assertEqual(session["history"], [])
        self.assertEqual(session["email"], "")
        
        # Modify session and verify persistence
        session["name"] = "Alice"
        session["state"] = "active"
        
        session2 = get_session(phone)
        self.assertEqual(session2["name"], "Alice")
        self.assertEqual(session2["state"], "active")

    def test_reset_session(self):
        phone = "0987654321"
        session = get_session(phone)
        session["name"] = "Bob"
        session["order"] = [{"product": "Test", "quantity": 1}]
        self.assertEqual(session["name"], "Bob")
        
        reset_session(phone)
        session2 = get_session(phone)
        self.assertEqual(session2["name"], "")
        self.assertEqual(session2["order"], [])
        self.assertEqual(session2["state"], "start")

if __name__ == '__main__':
    unittest.main()
