# ===============================
#          MAIN.PY — RENDER
# ===============================

import os
import asyncio
import threading
from flask import Flask, request

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
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
    get_appointments_today
)

from datetime import datetime


# ==========================================================
# GLOBAL EVENT LOOP FOR TELEGRAM
# ==========================================================

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

tg_app = ApplicationBuilder().token(BOT_TOKEN).build()

flask_app = Flask(__name__)

WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")
if WEBHOOK_URL:
    WEBHOOK_URL = WEBHOOK_URL.rstrip("/") + "/webhook"


# ==========================================================
# BOT HANDLERS
# ==========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🌸 خوش آمدید به *{CLINIC_NAME}*\n\n"
        f"🏥 آدرس: {CLINIC_ADDRESS}\n\n"
        "یک گزینه را انتخاب کنید:",
        reply_markup=main_menu_keyboard(update.effective_user.id in ADMINS),
        parse_mode="Markdown"
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer()

    if data == "show_doctors":
        docs = get_doctors()
        await query.edit_message_text(
            "👨‍⚕️ پزشکان:",
            reply_markup=doctor_keyboard(docs)
        )
        return

    if data == "show_services":
        srv = get_services()
        await query.edit_message_text(
            "🧴 خدمات:",
            reply_markup=services_keyboard(srv)
        )
        return

    if data == "admin_panel":
        today = get_appointments_today()
        text = "📋 نوبت‌های امروز:\n\n"
        if not today:
            text += "هیچی ثبت نشده."
        else:
            for t in today:
                text += f"👨‍⚕️ {t[0]} | 🧴 {t[1]} | ⏰ {t[2]}\n"

        await query.edit_message_text(text)
        return


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رسید دریافت شد 🌸")


# ==========================================================
# FLASK WEBHOOK ROUTE
# ==========================================================

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)

    update = Update.de_json(data, tg_app.bot)

    # اجرای آپدیت داخل event loop خود اپلیکیشن
    asyncio.run(tg_app.process_update(update))

    return "OK", 200



# ==========================================================
# START BOT + FLASK
# ==========================================================

def start_flask():
    flask_app.run(host="0.0.0.0", port=10000)


async def start_bot():
    create_tables()

    if WEBHOOK_URL:
        await tg_app.bot.set_webhook(WEBHOOK_URL)
        print("Webhook OK:", WEBHOOK_URL)

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(handle_callback))
    tg_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("BOT READY ON WEBHOOK...")


def main():
    # Thread فلask
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    # اجرای تلگرام
    loop.run_until_complete(start_bot())
    loop.run_forever()


if __name__ == "__main__":
    main()
