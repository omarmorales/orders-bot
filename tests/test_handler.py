import unittest
from unittest.mock import patch, MagicMock
from bot.handler import handle_message
from bot.sessions import reset_session, get_session

# Mock catalog for predictable testing
MOCK_PRODUCTS = [
    {
        "name": "Coca Cola 355ml",
        "unit_price": 15.0,
        "box_price": None,
        "units_per_box": None,
        "category": "Bebidas",
        "sells_by_box": False
    },
    {
        "name": "Aceite Nutrioli 946ml",
        "unit_price": 40.0,
        "box_price": 450.0,
        "units_per_box": 12,
        "category": "Abarrotes",
        "sells_by_box": True
    }
]

class TestHandler(unittest.TestCase):
    def setUp(self):
        self.phone = "test_123"
        reset_session(self.phone)
        
    @patch('bot.handler.products', MOCK_PRODUCTS)
    @patch('bot.handler.query_llm')
    def test_add_simple_product(self, mock_query_llm):
        # Setup mock LLM response
        mock_query_llm.return_value = {
            "accion": "buscar",
            "productos_encontrados": [{"nombre": "Coca Cola 355", "cantidad": 2, "presentacion": "pieza"}]
        }
        
        # Test welcome state
        response = handle_message(self.phone, "hola")
        self.assertIn("Cuál es tu *nombre*", response)
        
        # Test name capture
        response = handle_message(self.phone, "Juan")
        self.assertIn("Hola, *Juan*", response)
        self.assertEqual(get_session(self.phone)["name"], "Juan")
        
        # Query product
        response = handle_message(self.phone, "Quiero 2 cocas")
        
        # Verify the session was updated properly
        session = get_session(self.phone)
        self.assertEqual(len(session["order"]), 1)
        self.assertEqual(session["order"][0]["product"], "Coca Cola 355ml")
        self.assertEqual(session["order"][0]["quantity"], 2)

    @patch('bot.handler.products', MOCK_PRODUCTS)
    @patch('bot.handler.query_llm')
    def test_ambiguous_product_queue(self, mock_query_llm):
        session = get_session(self.phone)
        session["name"] = "Maria"
        session["state"] = "active"
        
        # LLM returns an ambiguous product (sells_by_box is True)
        mock_query_llm.return_value = {
            "accion": "buscar",
            "productos_encontrados": [
                {"nombre": "Aceite Nutrioli", "cantidad": 5, "presentacion": "pieza"},
                {"nombre": "Coca Cola 355", "cantidad": 1, "presentacion": "pieza"}
            ]
        }
        
        response = handle_message(self.phone, "5 aceites y 1 coca")
        
        # Should ask if piece or box for the FIRST ambiguous item (Aceite)
        self.assertIn("¿Lo quieres por *pieza* o por *caja*?", response)
        self.assertEqual(session["state"], "waiting_presentation")
        self.assertEqual(session["_temp_quantity"], 5)
        self.assertEqual(session["_temp_product"]["name"], "Aceite Nutrioli 946ml")
        
        # The Coca Cola should be queued in pending since it's simple or also processed? 
        # Actually Coca Cola sells_by_box=False, so it gets added immediately!
        # Let's check order length
        self.assertEqual(len(session["order"]), 1)
        self.assertEqual(session["order"][0]["product"], "Coca Cola 355ml")
        
        # Now Answer "caja" for the Aceite
        response = handle_message(self.phone, "caja")
        
        # Both should now be in the order
        self.assertEqual(len(session["order"]), 2)
        # The last added item should be the Aceite box
        self.assertEqual(session["order"][1]["is_box"], True)
        self.assertEqual(session["order"][1]["quantity"], 5)
        self.assertEqual(session["order"][1]["product"], "Aceite Nutrioli 946ml")
        self.assertEqual(session["state"], "active")

    @patch('bot.handler.notify_owner')
    @patch('bot.handler.notify_customer')
    @patch('bot.handler.products', MOCK_PRODUCTS)
    @patch('bot.handler.query_llm')
    def test_checkout_flow(self, mock_query_llm, mock_notify_customer, mock_notify_owner):
        session = get_session(self.phone)
        session["name"] = "Carlos"
        session["state"] = "active"
        
        # 1. User wants to confirm order
        mock_query_llm.return_value = {"accion": "confirmar", "mensaje": "Confirmando..."}
        
        # Bot says cart is empty if we try confirming now, so let's add an item manually to session
        session["order"] = [{
            "product": "Coca Cola 355ml",
            "quantity": 2,
            "subtotal": 30.0,
            "is_box": False
        }]
        
        response = handle_message(self.phone, "listo")
        self.assertEqual(session["state"], "confirming")
        self.assertIn("¿Confirmas tu pedido?", response)
        
        # 2. User says 'sí'
        response = handle_message(self.phone, "sí")
        self.assertEqual(session["state"], "waiting_payment_method")
        self.assertIn("¿Cómo prefieres pagar tu pedido?", response)
        
        # 3. User says 'Transferencia'
        response = handle_message(self.phone, "Transferencia")
        self.assertEqual(session["state"], "waiting_email")
        self.assertEqual(session["_payment_method"], "Transferencia")
        self.assertIn("CLABE: 012345678901234567", response)
        self.assertIn("¿Quieres recibir el resumen", response)
        
        # Check that owner was notified
        mock_notify_owner.assert_called_once_with("Carlos", self.phone, session["order"], "Transferencia")
        
        # 4. User provides an email
        response = handle_message(self.phone, "carlos@example.com")
        self.assertIn("Te enviamos el resumen", response)
        
        # Ensure session resets
        self.assertEqual(get_session(self.phone)["state"], "start")
        
        # Check that customer was notified
        mock_notify_customer.assert_called_once()
        args = mock_notify_customer.call_args[0]
        self.assertEqual(args[0], "Carlos")
        self.assertEqual(args[2], "carlos@example.com")
        self.assertEqual(args[4], "Transferencia")

if __name__ == '__main__':
    unittest.main()
