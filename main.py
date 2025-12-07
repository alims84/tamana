# ===============================
#          MAIN.PY — RENDER
# ===============================

import os
import asyncio
from flask import Flask, request

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
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
    get_appointments_today
)

from datetime import datetime


# ==========================================================
#               GLOBALS
# ==========================================================

flask_app = Flask(__name__)

# Loop اختصاصی برای پردازش Telegram
bot_loop = asyncio.new_event_loop()
asyncio.set_event_loop(bot_loop)

tg_app: Application = ApplicationBuilder().token(BOT_TOKEN).build()


# ==========================================================
#               TELEGRAM HANDLERS
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

    # رزرو نوبت
    if data == "book_appointment":
        now = datetime.now()
        buttons = []
        for i in range(7):
            d = now.replace(day=now.day + i)
            greg = d.strftime("%Y-%m-%d")
            j = jalali(d)
            buttons.append([InlineKeyboardButton(j, callback_data=f"day_{greg}")])

        await query.edit_message_text(
            "📅 انتخاب روز:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # انتخاب روز
    if data.startswith("day_"):
        context.user_data["selected_date"] = data.split("_")[1]
        await query.edit_message_text(
            "⏰ انتخاب ساعت:",
            reply_markup=time_keyboard()
        )
        return

    # انتخاب ساعت
    if data.startswith("time_"):
        context.user_data["selected_time"] = data.split("_")[1]
        await query.edit_message_text(
            "نوع پرداخت:",
            reply_markup=payment_keyboard()
        )
        return

    # پرداخت آنلاین
    if data == "pay_online":
        await query.edit_message_text("💳 در نسخه بعدی فعال می‌شود.")
        return

    # کارت‌به‌کارت
    if data == "pay_offline":
        await query.edit_message_text(card_to_card_text(), parse_mode="Markdown")
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



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رسید دریافت شد 🌸")


# ==========================================================
#               WEBHOOK ROUTE
# ==========================================================

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, tg_app.bot)

        # اجرای update در event loop اختصاصی
        asyncio.run_coroutine_threadsafe(
            tg_app.process_update(update),
            bot_loop
        )

        return "OK", 200
    except Exception as e:
        print("Webhook ERROR:", e)
        return "ERROR", 500


# ==========================================================
#               START BOT + FLASK
# ==========================================================

def start_bot():
    create_tables()

    # ثبت وبهوک
    external = os.environ.get("RENDER_EXTERNAL_URL")
    if external:
        url = external.rstrip("/") + "/webhook"
        bot_loop.run_until_complete(tg_app.bot.set_webhook(url))
        print("Webhook set:", url)

    # هندلرها
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(handle_callback))
    tg_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # اجرای bot در loop جدا
    bot_loop.create_task(tg_app.initialize())
    bot_loop.create_task(tg_app.start())


# اجرای Flask و Loop
if __name__ == "__main__":
    start_bot()
    flask_app.run(host="0.0.0.0", port=10000)
