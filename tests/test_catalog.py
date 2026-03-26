import unittest
from unittest.mock import patch
import bot.catalog as catalog

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

class TestCatalog(unittest.TestCase):

    @patch('bot.catalog.products', MOCK_PRODUCTS)
    def test_get_catalog_text(self):
        text = catalog.get_catalog_text()
        
        self.assertIn("Coca Cola 355ml (Category: Bebidas)", text)
        self.assertIn("Unit only: $15.00", text)
        
        self.assertIn("Aceite Nutrioli 946ml (Category: Abarrotes)", text)
        self.assertIn("Unit: $40.00 | Box (12 units): $450.00", text)

    @patch('bot.catalog.products', MOCK_PRODUCTS)
    def test_get_relevant_catalog_text(self):
        # Empty query
        text_empty = catalog.get_relevant_catalog_text("")
        self.assertIn("Coca Cola", text_empty) # With empty/very short queries fuzzy match might still return defaults
        
        # Specific query
        text_specific = catalog.get_relevant_catalog_text("aceite")
        self.assertIn("Aceite Nutrioli", text_specific)
        # Verify Coca Cola is NOT returned if top_k is 1 (though we default to 15, we can test exact length)
        text_limited = catalog.get_relevant_catalog_text("coca", top_k=1)
        self.assertIn("Coca Cola", text_limited)
        self.assertNotIn("Aceite Nutrioli", text_limited)

    # Note: We won't test `load_products` deeply since it requires reading the physical CSV, 
    # but we can test if it fails gracefully when the file doesn't exist by modifying CSV_PATH
    @patch('bot.catalog.CSV_PATH', 'invalid_path.csv')
    @patch('builtins.print')
    def test_load_products_file_not_found(self, mock_print):
        catalog.load_products()
        mock_print.assert_any_call("❌ File not found: invalid_path.csv")

if __name__ == '__main__':
    unittest.main()
