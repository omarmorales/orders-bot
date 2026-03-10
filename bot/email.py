# bot/email.py

import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import GMAIL_USER, GMAIL_PASSWORD, DUENO_EMAIL, SMTP_SERVER, SMTP_PORT


def is_valid_email(text):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", text.strip()))


def build_order_html(customer_name, phone_number, order):
    total = sum(i["subtotal"] for i in order)
    rows  = ""
    for item in order:
        presentation = "caja" if item.get("is_box") else "pieza"
        rows += f"""
        <tr>
            <td style="padding:8px;border-bottom:1px solid #eee">{item['product']}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center">{item['quantity']}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:center">{presentation}</td>
            <td style="padding:8px;border-bottom:1px solid #eee;text-align:right">${item['subtotal']:.2f}</td>
        </tr>"""

    return f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
        <h2 style="background:#25D366;color:white;padding:16px;border-radius:8px 8px 0 0;margin:0">
            🛒 Nuevo pedido — Abarrotes IBSA
        </h2>
        <div style="border:1px solid #ddd;border-top:none;padding:20px;border-radius:0 0 8px 8px">
            <p><strong>Cliente:</strong> {customer_name}</p>
            <p><strong>WhatsApp:</strong> {phone_number}</p>
            <table style="width:100%;border-collapse:collapse;margin-top:12px">
                <thead>
                    <tr style="background:#f5f5f5">
                        <th style="padding:8px;text-align:left">Producto</th>
                        <th style="padding:8px;text-align:center">Cantidad</th>
                        <th style="padding:8px;text-align:center">Presentación</th>
                        <th style="padding:8px;text-align:right">Subtotal</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            <p style="text-align:right;font-size:18px;margin-top:12px">
                <strong>Total: ${total:.2f}</strong>
            </p>
        </div>
    </div>"""


def send_email(recipient, subject, html_body):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = GMAIL_USER
        msg["To"]      = recipient
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, recipient, msg.as_string())

        print(f"📧 Email sent to {recipient}")
        return True
    except Exception as e:
        print(f"❌ Error sending email to {recipient}: {e}")
        return False


def notify_owner(customer_name, phone_number, order):
    html  = build_order_html(customer_name, phone_number, order)
    return send_email(DUENO_EMAIL, f"🛒 Nuevo pedido de {customer_name}", html)


def notify_customer(customer_name, phone_number, customer_email, order):
    html  = build_order_html(customer_name, phone_number, order)
    return send_email(customer_email, "Tu pedido en Abarrotes IBSA", html)