# interactive_test.py
from dotenv import load_dotenv
load_dotenv()

from bot.handler import handle_message

phone_number = "test_user"

print("🤖 Bot de pedidos - Modo prueba")
print("Escribe 'salir' para terminar\n")

while True:
    message = input("Tú: ").strip()
    if message.lower() == "salir":
        break
    response = handle_message(phone_number, message)
    print(f"\nBot: {response}\n")