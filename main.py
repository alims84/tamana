# ===============================
#     MAIN.PY — RENDER SAFE
# ===============================

import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from config import BOT_TOKEN, ADMINS, CLINIC_NAME, CLINIC_ADDRESS
from utils import (
    main_menu_keyboard,
    doctor_keyboard,
    services_keyboard,
    time_keyboard,
    payment_keyboard,
    card_to_card_text,
    jalali
)
from database import (
    create_tables,
    get_doctors,
    get_services,
    create_appointment,
    get_appointments_today
)

from datetime import datetime
import asyncio


# ============================
#   Flask
# ============================

flask_app = Flask(__name__)

WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")
if WEBHOOK_URL:
    WEBHOOK_URL = WEBHOOK_URL.rstrip("/") + "/webhook"


# ============================
#   Telegram Application
# ============================

tg_app = ApplicationBuilder().token(BOT_TOKEN).build()


# ============================
#   Handlers
# ============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id in ADMINS
    
    await update.message.reply_text(
        f"🌸 خوش آمدید به *{CLINIC_NAME}*\n\n"
        f"🏥 آدرس: {CLINIC_ADDRESS}\n\n"
        "لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=main_menu_keyboard(is_admin),
        parse_mode="Markdown"
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    if data == "show_doctors":
        await q.edit_message_text(
            "👨‍⚕️ پزشکان:",
            reply_markup=doctor_keyboard(get_doctors()),
            parse_mode="Markdown"
        )
        return

    if data == "show_services":
        await q.edit_message_text(
            "🧴 خدمات:",
            reply_markup=services_keyboard(get_services()),
            parse_mode="Markdown"
        )
        return

    if data == "back_main":
        await q.edit_message_text(
            "منوی اصلی:",
            reply_markup=main_menu_keyboard(q.from_user.id in ADMINS)
        )
        return


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رسید دریافت شد. 🌸")


# ============================
#   Webhook Endpoint
# ============================

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, tg_app.bot)
    # اجرای امن در Render
    asyncio.get_event_loop().create_task(tg_app.process_update(update))
    return "OK", 200


# ============================
#   Setup — Called Once
# ============================

async def setup():
    create_tables()

    if WEBHOOK_URL:
        await tg_app.bot.set_webhook(WEBHOOK_URL)
        print("Webhook set to:", WEBHOOK_URL)

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(handle_callback))
    tg_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))


# ============================
#   ENTRY POINT
# ============================

# Render executes Flask automatically
asyncio.get_event_loop().run_until_complete(setup())
print("BOT READY (WEBHOOK MODE)")
