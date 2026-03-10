# bot/cart.py

import unicodedata
from bot.catalog import products


def normalize(text):
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8').lower()


def get_order_summary(order):
    if not order:
        return "Tu carrito está vacío."
    lines = ["🛒 *Tu pedido:*\n"]
    total = 0
    for item in order:
        presentation = "caja" if item.get("is_box") else "pieza"
        lines.append(
            f"  • {item['quantity']}x {item['product']} ({presentation}) — ${item['subtotal']:.2f}"
        )
        total += item['subtotal']
    lines.append(f"\n💰 *Total: ${total:.2f}*")
    return "\n".join(lines)


def add_to_cart(session, prod, quantity, is_box):
    price    = prod["box_price"] if is_box else prod["unit_price"]
    subtotal = price * quantity

    existing = next(
        (i for i in session["order"]
         if i["product"] == prod["name"] and i.get("is_box") == is_box),
        None
    )
    if existing:
        existing["quantity"] += quantity
        existing["subtotal"] += subtotal
    else:
        session["order"].append({
            "product":  prod["name"],
            "quantity": quantity,
            "subtotal": subtotal,
            "is_box":   is_box,
        })

    presentation = "caja" if is_box else "pieza"
    return (
        f"✅ Agregado: *{quantity}x {prod['name']} ({presentation})* — ${subtotal:.2f}\n\n"
        + get_order_summary(session["order"])
        + "\n\n_Busca otro producto o escribe *listo* para confirmar._"
    )


def remove_from_cart(session, product_name):
    normalized = normalize(product_name)
    original   = session["order"][:]
    session["order"] = [
        i for i in session["order"]
        if normalize(i["product"]) != normalized
    ]
    if len(session["order"]) < len(original):
        return (
            f"🗑️ *{product_name.title()}* eliminado del carrito.\n\n"
            + get_order_summary(session["order"])
            + "\n\n_Sigue buscando o escribe *listo* para confirmar._"
        )
    return f"⚠️ No encontré *{product_name}* en tu carrito."


def update_cart_quantity(session, product_name, new_quantity, is_box):
    normalized = normalize(product_name)

    if new_quantity <= 0:
        return remove_from_cart(session, product_name)

    item = next(
        (i for i in session["order"]
         if normalize(i["product"]) == normalized and i.get("is_box") == is_box),
        None
    )
    if not item:
        return f"⚠️ No encontré *{product_name}* en tu carrito."

    prod = next((p for p in products if normalize(p["name"]) == normalized), None)
    if not prod:
        return f"⚠️ No encontré el precio de *{product_name}*."

    price            = prod["box_price"] if is_box else prod["unit_price"]
    item["quantity"] = new_quantity
    item["subtotal"] = price * new_quantity

    presentation = "caja" if is_box else "pieza"
    return (
        f"✏️ Actualizado: *{new_quantity}x {product_name.title()} ({presentation})*\n\n"
        + get_order_summary(session["order"])
        + "\n\n_Sigue buscando o escribe *listo* para confirmar._"
    )