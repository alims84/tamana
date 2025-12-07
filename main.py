# ===============================
#          MAIN.PY — RENDER
# ===============================

import os
import asyncio
from flask import Flask, request

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
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


# ==========================================================
#                     FLASK APP
# ==========================================================

WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")
if WEBHOOK_URL:
    WEBHOOK_URL = WEBHOOK_URL.rstrip("/") + "/webhook"

flask_app = Flask(__name__)

tg_app = ApplicationBuilder().token(BOT_TOKEN).build()


# ==========================================================
#                     BOT HANDLERS
# ==========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id in ADMINS

    await update.message.reply_text(
        f"🌸 خوش آمدید به *{CLINIC_NAME}*\n\n"
        f"🏥 آدرس: {CLINIC_ADDRESS}\n\n"
        "لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=main_menu_keyboard(is_admin),
        parse_mode="Markdown"
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    await query.answer()

    # بازگشت
    if data == "back_main":
        await query.edit_message_text(
            "منوی اصلی:",
            reply_markup=main_menu_keyboard(user_id in ADMINS)
        )
        return

    # پزشکان
    if data == "show_doctors":
        docs = get_doctors()
        await query.edit_message_text(
            "👨‍⚕️ *لیست پزشکان:*",
            reply_markup=doctor_keyboard(docs),
            parse_mode="Markdown"
        )
        return

    # خدمات
    if data == "show_services":
        srv = get_services()
        await query.edit_message_text(
            "🧴 *خدمات کلینیک:*",
            reply_markup=services_keyboard(srv),
            parse_mode="Markdown"
        )
        return

    # تاریخ
    if data == "book_appointment":
        now = datetime.now()
        msg = "📅 *انتخاب روز:*\n\n"
        buttons = []

        for i in range(7):
            d = now.replace(day=now.day + i)
            greg = d.strftime("%Y-%m-%d")
            j = jalali(d)
            buttons.append([InlineKeyboardButton(j, callback_data=f"day_{greg}")])

        await query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
        return

    # انتخاب روز
    if data.startswith("day_"):
        context.user_data["selected_date"] = data.split("_")[1]
        await query.edit_message_text(
            "⏰ *انتخاب ساعت:*",
            reply_markup=time_keyboard(),
            parse_mode="Markdown"
        )
        return

    # انتخاب ساعت
    if data.startswith("time_"):
        context.user_data["selected_time"] = data.split("_")[1]
        await query.edit_message_text(
            "نوع پرداخت را انتخاب کنید:",
            reply_markup=payment_keyboard()
        )
        return

    # پرداخت آنلاین
    if data == "pay_online":
        await query.edit_message_text(
            "💳 لینک پرداخت آنلاین در نسخه بعدی فعال می‌شود."
        )
        return

    # کارت‌به‌کارت
    if data == "pay_offline":
        await query.edit_message_text(
            card_to_card_text(),
            parse_mode="Markdown"
        )
        return

    # پنل مدیریت
    if data == "admin_panel":
        today = get_appointments_today()
        text = "📋 *نوبت‌های امروز:*\n\n"

        if not today:
            text += "هیچ نوبتی ثبت نشده."
        else:
            for t in today:
                text += f"👨‍⚕️ {t[0]} | 🧴 {t[1]} | ⏰ {t[2]}\n"

        await query.edit_message_text(text, parse_mode="Markdown")
        return


# ==========================================================
#    دریافت عکس رسید کارت‌به‌کارت
# ==========================================================

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رسید دریافت شد. نوبت شما ثبت شد. 🌸")


# ==========================================================
#               FLASK WEBHOOK ROUTE
# ==========================================================

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, tg_app.bot)
    asyncio.create_task(tg_app.process_update(update))
    return "OK", 200


# ==========================================================
#                     RUN BOT
# ==========================================================

async def run_bot():
    create_tables()

    if WEBHOOK_URL:
        await tg_app.bot.set_webhook(WEBHOOK_URL)
        print("Webhook set:", WEBHOOK_URL)

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(handle_callback))
    tg_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is running via Webhook...")

    await asyncio.get_event_loop().run_in_executor(
        None, flask_app.run, "0.0.0.0", 10000
    )


if __name__ == "__main__":
    asyncio.run(run_bot())
