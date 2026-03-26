# bot/__init__.py
from bot.sessions import get_session, reset_session
from bot.catalog import get_products, get_catalog_text
from bot.cart import add_to_cart, remove_from_cart, update_cart_quantity, get_order_summary
from bot.llm import query_llm
from bot.email import send_email, is_valid_email, build_order_html, notify_owner, notify_customer
from bot.handler import handle_message