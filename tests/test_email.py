import unittest
from unittest.mock import patch, MagicMock
from bot.email import is_valid_email, build_order_html, send_email

class TestEmail(unittest.TestCase):
    def test_is_valid_email(self):
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertTrue(is_valid_email("user.name+tag@domain.co.uk"))
        
        self.assertFalse(is_valid_email("invalid-email"))
        self.assertFalse(is_valid_email("test@.com"))
        self.assertFalse(is_valid_email("@example.com"))

    def test_build_order_html(self):
        order = [
            {"product": "Coca Cola", "quantity": 2, "subtotal": 30.0, "is_box": False},
            {"product": "Aceite", "quantity": 1, "subtotal": 450.0, "is_box": True}
        ]
        
        html = build_order_html("Carlos", "1234567890", order, "Efectivo")
        
        self.assertIn("Carlos", html)
        self.assertIn("1234567890", html)
        self.assertIn("Efectivo", html)
        self.assertIn("Coca Cola", html)
        self.assertIn("Aceite", html)
        self.assertIn("$480.00", html) # Total
        self.assertIn("pieza", html.lower())
        self.assertIn("caja", html.lower())

    @patch('bot.email.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp_class):
        mock_smtp = MagicMock()
        mock_smtp_class.return_value.__enter__.return_value = mock_smtp
        
        # Test sending an email via the synchronous inner loop
        import bot.email
        bot.email._send_email_task("test@example.com", "Test Subject", "<p>Test Body</p>")
        
        mock_smtp.sendmail.assert_called_once()
        args = mock_smtp.sendmail.call_args[0]
        self.assertEqual(args[1], "test@example.com")
        self.assertIn("Test Subject", args[2])

if __name__ == '__main__':
    unittest.main()
