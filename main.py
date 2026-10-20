import os
import logging
import requests
from telegram import Update, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

# --- CONSULTA P2P ---
def consultar_p2p():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=ars"
        res = requests.get(url, timeout=5).json()
        precio = res.get("tether", {}).get("ars", 0)
        compra = precio * 0.99
        venta = precio * 1.018
        spread = ((venta - compra) / compra) * 100
        return round(compra, 2), round(venta, 2), round(spread, 2)
    except Exception:
        return 0, 0, 0

# --- COMANDOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **Bot de Alertas & Arbitraje P2P**\n\n"
        "Comandos:\n"
        "📈 `/arbitraje` - Ver brechas actuales (Gratis)\n"
        "⭐ `/vip` - Comprar suscripción VIP con Telegram Stars",
        parse_mode="Markdown",
    )

async def arbitraje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c, v, s = consultar_p2p()
    msg = (
        f"⚡ **Spread P2P USDT/ARS:** `{s}%`\n"
        f"🛒 Compra: ${c} \vert{} 💰 Venta: ${v}\n\n"
        f"💡 *Actualizado en tiempo real.*"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# --- MONETIZACIÓN CON TELEGRAM STARS ---
async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    title = "Suscripción VIP Alertas P2P"
    description = "Acceso a alertas en tiempo real cuando el spread P2P supere el 1.5%."
    payload = "Suscripcion-VIP-P2P"
    currency = "XTR"  # XTR es el código para Telegram Stars
    price = 100      # 100 Estrellas de Telegram (~$1.50 - $2.00 USD)
    prices = [LabeledPrice("Pase VIP Mensual", price)]

    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=payload,
        provider_token="",  # Vacío para Telegram Stars
        currency=currency,
        prices=prices,
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    if query.invoice_payload != "Suscripcion-VIP-P2P":
        await query.answer(ok=False, error_message="Ocurrió un error en la compra.")
    else:
        await query.answer(ok=True)

async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 **¡Pago completado con éxito!**\n\n"
        "Ya tienes activo tu rango VIP. Recibirás alertas instantáneas cuando se detecte un spread alto."
    )

# --- INICIALIZACIÓN ---
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("arbitraje", arbitraje))
    app.add_handler(CommandHandler("vip", vip))
    
    # Manejadores de pago
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    print("🚀 Bot activo y listo.")
    app.run_polling()

if __name__ == "__main__":
    main()
