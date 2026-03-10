# bot/handler.py

from bot.sessions import get_session, reset_session
from bot.catalog import products
from bot.cart import add_to_cart, remove_from_cart, update_cart_quantity, get_order_summary, normalize
from bot.llm import query_llm
from bot.email import is_valid_email, notify_owner, notify_customer


def handle_message(phone_number, message):
    session = get_session(phone_number)

    # ── WELCOME ──
    if not session["name"] and session["state"] == "start":
        session["state"] = "waiting_name"
        return (
            "👋 ¡Bienvenido/a a *Abarrotes IBSA*!\n\n"
            "Soy tu asistente de pedidos 🤖\n\n"
            "¿Cuál es tu *nombre*?"
        )

    if session["state"] == "waiting_name":
        session["name"]  = message.strip().title()
        session["state"] = "active"
        return (
            f"¡Hola, *{session['name']}*! 😊\n\n"
            "Escribe el nombre del producto que buscas o dime qué necesitas.\n"
            "_Ej: 'refresco', 'una caja de arroz', 'detergente'..._\n\n"
            "_Escribe *0* para ver tu carrito o *listo* para confirmar._"
        )

    # ── QUICK COMMANDS ──
    if message.strip() == "0":
        return get_order_summary(session["order"]) + "\n\n_Sigue buscando o escribe *listo* para confirmar._"

    # ── WAITING FOR QUANTITY ──
    if session["state"] == "waiting_quantity":
        try:
            quantity = int(message.strip())
            if quantity <= 0:
                raise ValueError
            prod     = session["_temp_product"]
            is_box   = session.get("_is_box", False)
            session["state"] = "active"
            session.pop("_temp_product", None)
            session.pop("_is_box", None)
            return add_to_cart(session, prod, quantity, is_box)
        except ValueError:
            return "⚠️ Escribe un número válido mayor a 0."

    # ── WAITING FOR PRESENTATION ──
    if session["state"] == "waiting_presentation":
        msg  = message.strip().lower()
        prod = session["_temp_product"]

        if msg in ["caja", "c", "por caja"]:
            is_box = True
        elif msg in ["pieza", "p", "piezas", "por pieza", "suelto"]:
            is_box = False
        else:
            return (
                f"⚠️ No entendí. ¿Lo quieres por *pieza* (${prod['unit_price']:.2f}) "
                f"o por *caja* ({prod['units_per_box']} pzas — ${prod['box_price']:.2f})?"
            )

        session["_is_box"] = is_box
        session["state"]   = "waiting_quantity"
        presentation = "caja" if is_box else "pieza"
        return f"¿Cuántas *{presentation}s* de *{prod['name']}* quieres?"

    # ── SELECTING ──
    if session["state"] == "selecting":
        results = session.get("_results", [])
        try:
            idx = int(message.strip()) - 1
            if idx < 0 or idx >= len(results):
                raise ValueError
            prod = results[idx]
            session["_temp_product"] = prod

            if prod["sells_by_box"]:
                session["state"] = "waiting_presentation"
                return (
                    f"*{prod['name']}* disponible en:\n"
                    f"  • *Pieza* — ${prod['unit_price']:.2f}\n"
                    f"  • *Caja* ({prod['units_per_box']} pzas) — ${prod['box_price']:.2f}\n\n"
                    "¿Lo quieres por *pieza* o por *caja*?"
                )
            else:
                session["state"]  = "waiting_quantity"
                session["_is_box"] = False
                return f"¿Cuántas piezas de *{prod['name']}* quieres? (${prod['unit_price']:.2f} c/u)"

        except ValueError:
            return f"⚠️ Escribe un número entre 1 y {len(results)}."

    # ── CONFIRMING ──
    if session["state"] == "confirming":
        if message.strip().lower() in ["sí", "si", "s", "yes"]:
            summary      = get_order_summary(session["order"])
            name         = session["name"]
            order        = session["order"][:]

            # 📧 Notify owner
            notify_owner(name, phone_number, order)

            # Save order and wait for customer email
            session["_pending_order"] = order
            session["state"]          = "waiting_email"

            return (
                f"🎉 *¡Pedido confirmado, {name}!*\n\n"
                + summary
                + "\n\n¿Quieres recibir el resumen de tu pedido por correo?\n"
                "Escribe tu *email* o *no* si no lo deseas."
            )

        elif message.strip().lower() in ["no", "n"]:
            session["state"] = "active"
            return "De acuerdo, sigue buscando.\n\n_Escribe *listo* cuando termines._"
        else:
            return "Por favor responde *sí* o *no*."

    # ── WAITING FOR CUSTOMER EMAIL ──
    if session["state"] == "waiting_email":
        msg = message.strip().lower()

        if msg in ["no", "n"]:
            reset_session(phone_number)
            return (
                "👍 ¡De acuerdo! Tu pedido está confirmado.\n\n"
                "📞 *Abarrotes IBSA* — 444 821 2196\n"
                "📍 3a Norte 118, Central de Abastos\n"
                "San Luis Potosí, México\n\n"
                "🛍️ _¿Quieres hacer otro pedido? Solo escribe *hola* y empezamos de nuevo._"
            )

        if is_valid_email(message):
            pending_order = session.get("_pending_order", [])
            name          = session["name"]
            success       = notify_customer(name, phone_number, message.strip(), pending_order)
            reset_session(phone_number)

            if success:
                return (
                    f"📧 ¡Listo! Te enviamos el resumen a *{message.strip()}*\n\n"
                    "📞 *Abarrotes IBSA* — 444 821 2196\n"
                    "📍 3a Norte 118, Central de Abastos\n"
                    "San Luis Potosí, México\n\n"
                    "🛍️ _¿Quieres hacer otro pedido? Solo escribe *hola* y empezamos de nuevo._"
                )
            else:
                return (
                    "⚠️ No pudimos enviar el correo, pero tu pedido ya está confirmado.\n\n"
                    "📞 *Abarrotes IBSA* — 444 821 2196\n"
                    "📍 3a Norte 118, Central de Abastos\n"
                    "San Luis Potosí, México\n\n"
                    "🛍️ _¿Quieres hacer otro pedido? Solo escribe *hola* y empezamos de nuevo._"
                )

        return "⚠️ Ese correo no parece válido. Escríbelo de nuevo o escribe *no* para omitirlo."

    # ── QUERY LLM ──
    result       = query_llm(session, message)
    action       = result.get("accion", "conversar")
    found_products = result.get("productos_encontrados", [])
    llm_message  = result.get("mensaje", "")

    if action == "buscar":
        if not found_products:
            return llm_message

        matched = []
        for item in found_products:
            name         = item.get("nombre", "")            if isinstance(item, dict) else item
            quantity     = item.get("cantidad", 1)           if isinstance(item, dict) else 1
            presentation = item.get("presentacion", "pieza") if isinstance(item, dict) else "pieza"
            prod = next((p for p in products if normalize(p["name"]) == normalize(name)), None)
            if prod:
                matched.append({
                    "prod":         prod,
                    "quantity":     quantity,
                    "presentation": presentation,
                })

        if not matched:
            return llm_message

        if len(matched) == 1:
            item = matched[0]
            prod = item["prod"]
            session["_temp_product"] = prod

            if item["presentation"] == "caja" and prod["sells_by_box"]:
                session["_is_box"] = True
                session["state"]   = "waiting_quantity"
                return f"¿Cuántas *cajas* de *{prod['name']}* quieres? ({prod['units_per_box']} pzas — ${prod['box_price']:.2f} c/u)"

            if prod["sells_by_box"]:
                session["state"] = "waiting_presentation"
                return (
                    f"*{prod['name']}* disponible en:\n"
                    f"  • *Pieza* — ${prod['unit_price']:.2f}\n"
                    f"  • *Caja* ({prod['units_per_box']} pzas) — ${prod['box_price']:.2f}\n\n"
                    "¿Lo quieres por *pieza* o por *caja*?"
                )
            else:
                session["_is_box"] = False
                session["state"]   = "waiting_quantity"
                return f"¿Cuántas piezas de *{prod['name']}* quieres? (${prod['unit_price']:.2f} c/u)"

        responses = []
        pending   = []

        for item in matched:
            prod         = item["prod"]
            quantity     = item["quantity"]
            presentation = item["presentation"]
            is_box       = presentation == "caja" and prod["sells_by_box"]

            if prod["sells_by_box"] and presentation == "pieza":
                pending.append(prod)
            else:
                responses.append(add_to_cart(session, prod, quantity, is_box))

        if pending:
            prod = pending[0]
            session["_temp_product"] = prod
            session["_pending_prods"] = pending[1:]
            session["state"]          = "waiting_presentation"
            text = get_order_summary(session["order"]) + "\n\n" if session["order"] else ""
            return (
                text
                + f"*{prod['name']}* disponible en:\n"
                f"  • *Pieza* — ${prod['unit_price']:.2f}\n"
                f"  • *Caja* ({prod['units_per_box']} pzas) — ${prod['box_price']:.2f}\n\n"
                "¿Lo quieres por *pieza* o por *caja*?"
            )

        return responses[-1] if responses else llm_message

    if action == "eliminar":
        if not found_products:
            return "⚠️ No entendí qué producto quieres quitar. Dime el nombre."
        name = found_products[0].get("nombre", "") if isinstance(found_products[0], dict) else found_products[0]
        return remove_from_cart(session, name)

    if action == "modificar":
        if not found_products:
            return "⚠️ No entendí qué producto quieres modificar. Dime el nombre y la nueva cantidad."
        item     = found_products[0] if isinstance(found_products[0], dict) else {"nombre": found_products[0]}
        name     = item.get("nombre", "")
        quantity = int(item.get("cantidad", 1))
        is_box   = item.get("presentacion", "pieza") == "caja"
        return update_cart_quantity(session, name, quantity, is_box)

    if action == "confirmar":
        if not session["order"]:
            return "⚠️ Tu carrito está vacío. Busca algún producto primero."
        session["state"] = "confirming"
        return get_order_summary(session["order"]) + "\n\n¿Confirmas tu pedido? Escribe *sí* o *no*."

    if action == "cancelar":
        reset_session(phone_number)
        return "❌ Pedido cancelado. Escribe *hola* para empezar de nuevo."

    if action == "ver_carrito":
        return get_order_summary(session["order"]) + "\n\n_Escribe *listo* para confirmar._"

    return llm_message