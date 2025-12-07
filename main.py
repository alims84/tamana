# ===============================
#       MAIN.PY — RENDER OK
# ===============================

import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from datetime import datetime

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


# -----------------------------
# Flask App
# -----------------------------
flask_app = Flask(__name__)

WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")
if WEBHOOK_URL:
    WEBHOOK_URL = WEBHOOK_URL.rstrip("/") + "/webhook"


# -----------------------------
# Build Telegram Application
# -----------------------------
tg_app: Application = ApplicationBuilder().token(BOT_TOKEN).build()


# -----------------------------
# Start Handler
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_admin = update.effective_user.id in ADMINS

    await update.message.reply_text(
        f"🌸 خوش آمدید به *{CLINIC_NAME}*\n\n"
        f"🏥 آدرس: {CLINIC_ADDRESS}\n\n"
        "لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=main_menu_keyboard(is_admin),
        parse_mode="Markdown"
    )


# -----------------------------
# Callback Handler
# -----------------------------
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    data = q.data
    await q.answer()

    if data == "back_main":
        await q.edit_message_text(
            "منوی اصلی:",
            reply_markup=main_menu_keyboard(q.from_user.id in ADMINS)
        )
        return

    if data == "show_doctors":
        docs = get_doctors()
        await q.edit_message_text(
            "👨‍⚕️ *لیست پزشکان:*",
            reply_markup=doctor_keyboard(docs),
            parse_mode="Markdown"
        )
        return

    if data == "show_services":
        srv = get_services()
        await q.edit_message_text(
            "🧴 *خدمات کلینیک:*",
            reply_markup=services_keyboard(srv),
            parse_mode="Markdown"
        )
        return


# -----------------------------
# Photo Handler
# -----------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رسید دریافت شد. 🌸")


# -----------------------------
# Webhook Route
# -----------------------------
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, tg_app.bot)

    # اجرای مستقیم update بدون create_task
    asyncio.run(tg_app.process_update(update))

    return "OK", 200


# -----------------------------
# Setup Function
# -----------------------------
async def setup():
    create_tables()

    if WEBHOOK_URL:
        await tg_app.bot.set_webhook(WEBHOOK_URL)
        print("Webhook OK:", WEBHOOK_URL)

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(handle_callback))
    tg_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))


# -----------------------------
# Entry Point — Render runs Flask automatically
# -----------------------------
asyncio.run(setup())
