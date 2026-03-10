# bot/llm.py

import json
from openai import OpenAI
from config import OPENAI_API_KEY
from bot.catalog import get_catalog_text

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL  = "gpt-4o-mini"


def query_llm(session, user_message):
    system_prompt = f"""You are a message classifier for an order system of a grocery store.
The store and customers communicate in Spanish, so all responses must be in Spanish.

CATALOG:
{get_catalog_text()}

Respond ONLY with JSON, no additional text:
{{"accion": "buscar", "productos_encontrados": [{{"nombre": "", "cantidad": 1, "presentacion": "pieza"}}], "mensaje": ""}}

RULES:
- accion is ALWAYS "buscar" when the customer mentions products from the catalog.
- accion is "confirmar" ONLY if the customer says: "listo", "confirmar", "eso es todo", "terminar".
- accion is "ver_carrito" ONLY if they say "ver carrito" or "mi pedido".
- accion is "cancelar" ONLY if they say "cancelar".
- accion is "eliminar" ONLY if the customer wants to remove a product from the cart.
- accion is "modificar" ONLY if the customer wants to change the quantity of a product in the cart.
- accion is "conversar" for greetings or general questions.
- productos_encontrados: list with the EXACT name from the catalog, quantity and presentacion ("pieza" or "caja").
- If the customer does not mention presentacion, use "pieza" by default.
- If the customer does not mention quantity, use 1 by default.
- mensaje: short and friendly response in Spanish.
"""

    session["history"].append({"role": "user", "content": user_message})
    history = session["history"][-6:]

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}] + history,
        temperature=0,
        response_format={"type": "json_object"},
    )

    response_text = response.choices[0].message.content
    print(f"\n🔍 DEBUG OpenAI: {response_text}\n")
    session["history"].append({"role": "assistant", "content": response_text})

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {
            "accion":                "conversar",
            "productos_encontrados": [],
            "mensaje":               response_text
        }