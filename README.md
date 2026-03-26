# 🛒 WhatsApp Order Bot

A WhatsApp chatbot for **Abarrotes IBSA** that allows customers to place orders through WhatsApp. Built with Python, Flask, Twilio, and OpenAI GPT-4o Mini.

---

## ✨ Features

- 💬 Conversational order flow via WhatsApp
- 🤖 Natural language understanding powered by GPT-4o Mini
- 🛍️ Add, remove, and update products in the cart
- 📦 Support for unit and box pricing
- 📧 Automatic email notifications to the store owner on every order
- 📧 Optional order summary email sent to the customer
- 📄 Product catalog loaded from a CSV file with hot-reload on changes
- 🔄 Auto-reload catalog when `products.csv` is updated (no restart needed)

---

## 🗂️ Project Structure

```
orders-bot/
│
├── app.py                  # Flask server and routes
├── config.py               # Credentials (never commit this file)
├── config.example.py       # Credentials template
├── products.csv           # Product catalog
├── requirements.txt        # Python dependencies
├── interactive_test.py     # Local interactive test script
│
└── bot/
    ├── __init__.py         # Module exports
    ├── sessions.py         # Session state management
    ├── catalog.py          # CSV loader and catalog watcher
    ├── cart.py             # Cart operations
    ├── llm.py              # OpenAI GPT-4o Mini integration
    ├── email.py            # Email notifications
    └── handler.py          # Main message processing logic
```

---

## ⚙️ Requirements

### Accounts and API Keys

| Service | Purpose | Link |
|---|---|---|
| **Twilio** | WhatsApp messaging | [twilio.com](https://twilio.com) |
| **OpenAI** | Natural language understanding | [platform.openai.com](https://platform.openai.com) |
| **Gmail** | Email notifications | [myaccount.google.com](https://myaccount.google.com) |

### Gmail Setup
1. Enable **2-Step Verification** on your Google account
2. Go to **My Account → Security → App Passwords**
3. Generate an App Password for "Mail"
4. Use that 16-character password in `config.py` — **not** your regular Gmail password

### Twilio Setup
1. Create a Twilio account
2. Go to **Messaging → Try it out → Send a WhatsApp message**
3. Follow the sandbox setup instructions
4. Note your **Account SID** and **Auth Token** from the dashboard

### OpenAI Setup
1. Create an account at [platform.openai.com](https://platform.openai.com)
2. Go to **Billing** and add a payment method (minimum $5 USD)
3. Go to **API Keys → Create new secret key**

---

## 🚀 Local Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/orders-bot.git
cd orders-bot
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up credentials
```bash
cp config.example.py config.py
```

Then open `config.py` and fill in your credentials:
```python
OPENAI_API_KEY     = "sk-..."
GMAIL_USER         = "your@gmail.com"
GMAIL_PASSWORD     = "xxxx xxxx xxxx xxxx"  # Gmail App Password
DUENO_EMAIL        = "owner@gmail.com"
SMTP_SERVER        = "smtp.gmail.com"
SMTP_PORT          = 587
TWILIO_ACCOUNT_SID = "AC..."
TWILIO_AUTH_TOKEN  = "..."
```

### 5. Set up the product catalog
Create a `products.csv` file in the root of the project with this format:

```csv
nombre,precio_pieza,precio_caja,piezas_caja,categoria,venta_caja
Arroz,5.50,60.00,12,Granos,true
Frijol,6.00,65.00,12,Granos,true
Detergente,18.00,,,Limpieza,false
Refresco Cola,15.00,160.00,12,Bebidas,true
```

| Column | Description |
|---|---|
| `nombre` | Product name |
| `precio_pieza` | Unit price |
| `precio_caja` | Box price (leave empty if not sold by box) |
| `piezas_caja` | Units per box (leave empty if not sold by box) |
| `categoria` | Product category |
| `venta_caja` | `true` if sold by box, `false` if unit only |

---

## 🧪 Testing Locally

### Interactive Testing

Run the interactive test script — no Twilio or ngrok needed:

```bash
python interactive_test.py
```

Example conversation:
```
Tú: hola
Bot: 👋 ¡Bienvenido/a a Abarrotes IBSA!... ¿Cuál es tu nombre?

Tú: Juan
Bot: ¡Hola, Juan! 😊 ...

Tú: quiero arroz
Bot: *Arroz* disponible en: ...

Tú: pieza
Bot: ¿Cuántas piezas de Arroz quieres?

Tú: 3
Bot: ✅ Agregado: 3x Arroz...

Tú: listo
Bot: 🛒 Tu pedido... ¿Confirmas?

Tú: si
Bot: 🎉 ¡Pedido confirmado!
```

### Automated Unit Tests

To run the automated tests that verify the internal state machine without making live AI requests, run:

```bash
python -m unittest discover tests/
```

---

## 📡 Running with Twilio Sandbox

### 1. Start the server
```bash
python app.py
```

### 2. Expose your local server with ngrok
```bash
ngrok http 5001
```

Copy the `https://xxxx.ngrok.io` URL.

### 3. Configure the webhook in Twilio
Go to **Twilio Console → Messaging → Sandbox Settings** and set:
```
https://xxxx.ngrok.io/whatsapp
```

### 4. Connect your WhatsApp
Send the sandbox join message (e.g. `join <word>`) to the Twilio sandbox number from your WhatsApp.

> ⚠️ ngrok generates a new URL every time it restarts — update the Twilio webhook accordingly.

---

## 💬 Bot Commands

| Command | Action |
|---|---|
| `hola` | Start a new order |
| `0` | View current cart |
| `listo` | Confirm order |
| `cancelar` | Cancel and reset session |
| `ver carrito` | View current cart |
| `quita [product]` | Remove product from cart |
| `cambia [product] a [qty]` | Update product quantity |

---

## 📬 Contact

**Abarrotes IBSA**
📞 444 821 2196
📍 3a Norte 118, Central de Abastos, San Luis Potosí, México