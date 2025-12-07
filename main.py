# ============================
#         MAIN.PY
# ============================

import logging
import asyncio
import datetime
from flask import Flask, request

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from config import BOT_TOKEN, ADMINS
from database import (
    create_tables,
    get_doctors,
    get_services,
    add_appointment
)
from utils import (
    main_menu_keyboard,
    doctors_keyboard,
    services_keyboard,
    payment_keyboard,
    card_to_card_text,
    to_jalali
)

# ------------------ LOGGING ------------------

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


# ------------------ FLASK FOR WEBHOOK ------------------

app = Flask(__name__)
tg_app = None


@app.post("/webhook")
async def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return "OK", 200


# ------------------ START ------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id in ADMINS

    await update.message.reply_text(
        f"سلام {update.effective_user.first_name} 🌸",
        reply_markup=main_menu_keyboard(is_admin)
    )


# ------------------ CALLBACKS ------------------

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    # ----- BACK -----
    if data == "back_main":
        is_admin = query.from_user.id in ADMINS
        await query.edit_message_text(
            "منوی اصلی:",
            reply_markup=main_menu_keyboard(is_admin)
        )
        return

    # ----- DOCTORS -----
    if data == "doctors":
        docs = get_doctors()
        await query.edit_message_text(
            "لیست پزشکان:",
            reply_markup=doctors_keyboard(docs)
        )
        return

    # ----- SERVICES -----
    if data == "services":
        items = get_services()
        await query.edit_message_text(
            "لیست خدمات:",
            reply_markup=services_keyboard(items)
        )
        return

    # ----- ABOUT -----
    if data == "about":
        await query.edit_message_text(
            "کلینیک زیبایی تمارا\nبهترین خدمات زیبایی ✨",
            reply_markup=main_menu_keyboard(query.from_user.id in ADMINS)
        )
        return

    # ----- PAYMENT -----
    if data == "pay_manual":
        await query.edit_message_text(
            card_to_card_text(),
            reply_markup=payment_keyboard()
        )
        return


# ------------------ RUN BOT ------------------

async def run_bot():
    global tg_app

    create_tables()

    tg_app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(callbacks))

    # Set webhook
    await tg_app.bot.set_webhook("https://tamana.onrender.com/webhook")

    log.info("Bot is running (Webhook)...")
    await tg_app.start()
    await tg_app.updater.start_polling()  # required fix on render


# ------------------ FLASK SERVER ------------------

def run_flask():
    app.run(host="0.0.0.0", port=10000)


# ------------------ ENTRY ------------------

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    run_flask()
