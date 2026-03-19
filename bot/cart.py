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
    if not session["order"]:
        return f"⚠️ No encontré *{product_name}* en tu carrito."

    from thefuzz import process
    cart_names = [i["product"] for i in session["order"]]
    best_match = process.extractOne(product_name, cart_names, score_cutoff=70)

    if not best_match:
        return f"⚠️ No encontré *{product_name}* en tu carrito."

    matched_name = best_match[0]
    original = session["order"][:]
    session["order"] = [i for i in session["order"] if i["product"] != matched_name]

    return (
        f"🗑️ *{matched_name.title()}* eliminado del carrito.\n\n"
        + get_order_summary(session["order"])
        + "\n\n_Sigue buscando o escribe *listo* para confirmar._"
    )


def update_cart_quantity(session, product_name, new_quantity, is_box):
    if new_quantity <= 0:
        return remove_from_cart(session, product_name)

    if not session["order"]:
        return f"⚠️ No encontré *{product_name}* en tu carrito."

    from thefuzz import process
    cart_names = [i["product"] for i in session["order"]]
    best_match = process.extractOne(product_name, cart_names, score_cutoff=70)

    if not best_match:
        return f"⚠️ No encontré *{product_name}* en tu carrito."

    matched_name = best_match[0]

    item = next(
        (i for i in session["order"]
         if i["product"] == matched_name and i.get("is_box") == is_box),
        None
    )
    if not item:
        return f"⚠️ No encontré *{matched_name}* en tu carrito."

    prod = next((p for p in products if p["name"] == matched_name), None)
    if not prod:
        return f"⚠️ No encontré el precio de *{matched_name}*."

    price            = prod["box_price"] if is_box else prod["unit_price"]
    item["quantity"] = new_quantity
    item["subtotal"] = price * new_quantity

    presentation = "caja" if is_box else "pieza"
    return (
        f"✏️ Actualizado: *{new_quantity}x {product_name.title()} ({presentation})*\n\n"
        + get_order_summary(session["order"])
        + "\n\n_Sigue buscando o escribe *listo* para confirmar._"
    )