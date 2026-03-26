import unittest
from unittest.mock import patch, MagicMock
from bot.llm import query_llm

class TestLLM(unittest.TestCase):
    def setUp(self):
        self.session = {"history": []}

    @patch('bot.llm.client.chat.completions.create')
    @patch('bot.llm.get_relevant_catalog_text')
    def test_query_llm_valid_json(self, mock_get_catalog, mock_openai_create):
        mock_get_catalog.return_value = "- Coca Cola (Category: Bebidas) — Unit only: $15.00"
        
        # Mocking the OpenAI response object structure
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"accion": "buscar", "productos_encontrados": [{"nombre": "Coca Cola"}], "mensaje": "Aquí tienes"}'
        mock_openai_create.return_value = mock_response

        result = query_llm(self.session, "quiero una coca")
        
        self.assertEqual(result["accion"], "buscar")
        self.assertEqual(result["productos_encontrados"][0]["nombre"], "Coca Cola")
        self.assertEqual(result["mensaje"], "Aquí tienes")
        self.assertEqual(len(self.session["history"]), 2) # user and assistant

    @patch('bot.llm.client.chat.completions.create')
    @patch('bot.llm.get_relevant_catalog_text')
    def test_query_llm_invalid_json_fallback(self, mock_get_catalog, mock_openai_create):
        mock_get_catalog.return_value = ""
        
        # Mocking the OpenAI response to return invalid JSON
        mock_response = MagicMock()
        mock_response.choices[0].message.content = 'Hola, no soy JSON'
        mock_openai_create.return_value = mock_response

        result = query_llm(self.session, "hola")
        
        self.assertEqual(result["accion"], "conversar")
        self.assertEqual(result["productos_encontrados"], [])
        self.assertEqual(result["mensaje"], "Hola, no soy JSON")

if __name__ == '__main__':
    unittest.main()
