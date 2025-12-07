import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CallbackQueryHandler,
    CommandHandler, ContextTypes
)
from config import BOT_TOKEN, ADMIN_IDS, WEBHOOK_URL
from database import *
from utils import *
from datetime import datetime

create_tables()

app = Flask(__name__)

tg_app = ApplicationBuilder().token(BOT_TOKEN).build()


# -----------------------
# /start
# -----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = user.id in ADMIN_IDS

    await update.message.reply_text(
        f"سلام {user.first_name} 🌸",
        reply_markup=main_menu_keyboard(is_admin)
    )


# -----------------------
# دکمه‌ها
# -----------------------
async def buttons(update: Update, context):
    q = update.callback_query
    data = q.data
    await q.answer()

    # برگشت
    if data == "back_main":
        return await q.message.edit_text(
            "منوی اصلی:",
            reply_markup=main_menu_keyboard(q.from_user.id in ADMIN_IDS)
        )

    # پزشکان
    if data == "doctors":
        return await q.message.edit_text(
            "لیست پزشکان:",
            reply_markup=doctor_keyboard(get_doctors())
        )

    # خدمات
    if data == "services":
        return await q.message.edit_text(
            "لیست خدمات:",
            reply_markup=services_keyboard(get_services())
        )

    # درباره
    if data == "about":
        return await q.message.edit_text("کلینیک زیبایی تامارا ✨")

    # ادمین
    if data == "admin_panel":
        return await q.message.edit_text("⚙️ پنل مدیریت", reply_markup=None)


# -----------------------
# Webhook Handler
# -----------------------
@app.post("/webhook")
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    asyncio.get_event_loop().create_task(tg_app.process_update(update))
    return "OK"


# -----------------------
# اجرای ربات
# -----------------------
async def run_bot():
    await tg_app.initialize()
    await tg_app.start()
    await tg_app.bot.set_webhook(WEBHOOK_URL)
    print("Bot is running via Webhook...")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(run_bot())
    app.run(host="0.0.0.0", port=10000)
