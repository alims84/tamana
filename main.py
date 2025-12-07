import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import BOT_TOKEN
from utils import main_menu_keyboard
from database import (
    get_doctors,
    get_services,
)

# ---------------------------
# FLASK APP  (Render Webhook)
# ---------------------------

app = Flask(__name__)
telegram_app = None   # در ادامه مقداردهی می‌شود


# ---------------------------
#   COMMANDS
# ---------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام 👋\nبه ربات کلینیک زیبایی تمارا خوش آمدید 🌸",
        reply_markup=main_menu_keyboard(False)
    )


# ---------------------------
#   CALLBACKS
# ---------------------------

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # ---- Doctors ----
    if data == "show_doctors":
        doctors = get_doctors()
        text = "👨‍⚕️ *پزشکان کلینیک*\n\n"
        for d in doctors:
            text += f"• {d[1]} — {d[2]}\n"
        await query.edit_message_text(text, parse_mode="Markdown")
        return

    # ---- Services ----
    if data == "show_services":
        services = get_services()
        text = "🧴 *لیست خدمات*\n\n"
        for s in services:
            text += f"• {s}\n"
        await query.edit_message_text(text, parse_mode="Markdown")
        return

    # ---- Back ----
    if data == "back_main":
        await query.edit_message_text(
            "منوی اصلی:",
            reply_markup=main_menu_keyboard(False)
        )
        return


# ---------------------------
#   FLASK ENDPOINT
# ---------------------------

@app.post("/webhook")
async def webhook():
    """Telegram sends updates here"""
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK", 200


# ---------------------------
#   INIT BOT (NO POLLING)
# ---------------------------

async def init_bot():
    global telegram_app

    telegram_app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Handlers
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(handle_callback))
    telegram_app.add_handler(MessageHandler(filters.TEXT, start))

    # Set Webhook
    webhook_url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"

    await telegram_app.bot.set_webhook(webhook_url)
    print("Webhook set:", webhook_url)

    return telegram_app


# ---------------------------
# RUN APP (Render)
# ---------------------------

if __name__ == "__main__":
    print("🔥 Starting webhook bot...")

    # اجرای bot در event loop مستقل
    loop = asyncio.get_event_loop()

    loop.run_until_complete(init_bot())

    # اجرای Flask (blocking)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
