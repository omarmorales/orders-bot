# app.py

from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os

from bot.catalog import start_catalog_watcher
from bot.handler import handle_message
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

load_dotenv()

# ── Twilio ──
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# ── Flask ──
app = Flask(__name__)

# ── Catalog watcher ──
observer = start_catalog_watcher()


@app.route('/whatsapp', methods=["POST"])
def whatsapp_route():
    phone_number = request.form.get("From")
    message      = request.form.get("Body")
    print(f">>> {phone_number}: {message}")

    response = handle_message(phone_number, message)

    resp = MessagingResponse()
    resp.message(response)
    return str(resp), 200, {"Content-Type": "text/xml"}


if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5001)
    finally:
        observer.stop()
        observer.join()