import unittest
from unittest.mock import patch
from bot.cart import get_order_summary, add_to_cart, remove_from_cart, update_cart_quantity

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

class TestCart(unittest.TestCase):
    def setUp(self):
        self.session = {"order": []}

    def test_get_order_summary_empty(self):
        result = get_order_summary(self.session["order"])
        self.assertEqual(result, "Tu carrito está vacío.")

    def test_get_order_summary_with_items(self):
        self.session["order"] = [
            {"product": "Coca Cola 355ml", "quantity": 2, "subtotal": 30.0, "is_box": False},
            {"product": "Aceite Nutrioli 946ml", "quantity": 1, "subtotal": 450.0, "is_box": True}
        ]
        result = get_order_summary(self.session["order"])
        self.assertIn("2x Coca Cola 355ml (pieza) — $30.00", result)
        self.assertIn("1x Aceite Nutrioli 946ml (caja) — $450.00", result)
        self.assertIn("Total: $480.00", result)

    def test_add_to_cart_new_item(self):
        prod = MOCK_PRODUCTS[0]
        result = add_to_cart(self.session, prod, 3, False)
        
        self.assertEqual(len(self.session["order"]), 1)
        self.assertEqual(self.session["order"][0]["quantity"], 3)
        self.assertEqual(self.session["order"][0]["subtotal"], 45.0)
        self.assertIn("Agregado", result)
        self.assertIn("3x Coca Cola 355ml (pieza)", result)

    def test_add_to_cart_existing_item(self):
        prod = MOCK_PRODUCTS[0]
        # First add
        add_to_cart(self.session, prod, 2, False)
        # Second add
        add_to_cart(self.session, prod, 3, False)
        
        self.assertEqual(len(self.session["order"]), 1)
        self.assertEqual(self.session["order"][0]["quantity"], 5)
        self.assertEqual(self.session["order"][0]["subtotal"], 75.0)

    def test_add_to_cart_box(self):
        prod = MOCK_PRODUCTS[1]
        add_to_cart(self.session, prod, 2, True)
        
        self.assertEqual(self.session["order"][0]["quantity"], 2)
        self.assertEqual(self.session["order"][0]["subtotal"], 900.0) # 450 * 2
        self.assertTrue(self.session["order"][0]["is_box"])

    def test_remove_from_cart_empty(self):
        result = remove_from_cart(self.session, "Coca")
        self.assertIn("No encontré *Coca* en tu carrito.", result)

    def test_remove_from_cart_fuzzy(self):
        self.session["order"] = [
            {"product": "Coca Cola 355ml", "quantity": 2, "subtotal": 30.0, "is_box": False}
        ]
        result = remove_from_cart(self.session, "coca cola")
        self.assertEqual(len(self.session["order"]), 0)
        self.assertIn("eliminado del carrito", result)

    @patch('bot.cart.get_products', new=lambda: MOCK_PRODUCTS)
    def test_update_cart_quantity(self):
        self.session["order"] = [
            {"product": "Coca Cola 355ml", "quantity": 2, "subtotal": 30.0, "is_box": False}
        ]
        
        # Update to 5 units
        result = update_cart_quantity(self.session, "coca", 5, False)
        self.assertEqual(self.session["order"][0]["quantity"], 5)
        self.assertEqual(self.session["order"][0]["subtotal"], 75.0)
        self.assertIn("Actualizado: *5x Coca", result)

    @patch('bot.cart.get_products', new=lambda: MOCK_PRODUCTS)
    def test_update_cart_quantity_zero_removes_item(self):
        self.session["order"] = [
            {"product": "Coca Cola 355ml", "quantity": 2, "subtotal": 30.0, "is_box": False}
        ]
        
        # Update to 0 removes the item
        result = update_cart_quantity(self.session, "coca", 0, False)
        self.assertEqual(len(self.session["order"]), 0)
        self.assertIn("eliminado del carrito", result)

if __name__ == '__main__':
    unittest.main()
