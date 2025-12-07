
# ===============================================
#                MAIN.PY  (Render Webhook)
# ===============================================

import os
import asyncio
from flask import Flask, request
from datetime import datetime
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
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


# =====================================================
#               FLASK + TELEGRAM APP
# =====================================================

flask_app = Flask(__name__)

WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")
if WEBHOOK_URL:
    WEBHOOK_URL = WEBHOOK_URL.rstrip("/") + "/webhook"

tg_app = ApplicationBuilder().token(BOT_TOKEN).build()


# =====================================================
#                 BOT HANDLERS
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id in ADMINS

    await update.message.reply_text(
        f"🌸 خوش آمدید به *{CLINIC_NAME}*\n"
        f"🏥 {CLINIC_ADDRESS}\n\n"
        "لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=main_menu_keyboard(is_admin),
        parse_mode="Markdown"
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    await query.answer()

    # ------------------ بازگشت ------------------
    if data == "back_main":
        await query.edit_message_text(
            "منوی اصلی:",
            reply_markup=main_menu_keyboard(user_id in ADMINS)
        )
        return

    # ------------------ پزشکان ------------------
    if data == "show_doctors":
        docs = get_doctors()
        await query.edit_message_text(
            "👨‍⚕️ *لیست پزشکان:*",
            reply_markup=doctor_keyboard(docs),
            parse_mode="Markdown"
        )
        return

    # ------------------ خدمات ------------------
    if data == "show_services":
        srv = get_services()
        await query.edit_message_text(
            "🧴 *خدمات:*",
            reply_markup=services_keyboard(srv),
            parse_mode="Markdown"
        )
        return

    # ------------------ رزرو - انتخاب تاریخ ------------------
    if data == "book":
        now = datetime.now()
        buttons = []
        for i in range(7):
            d = now.replace(day=now.day + i)
            greg = d.strftime("%Y-%m-%d")
            buttons.append([InlineKeyboardButton(jalali(d), callback_data=f"day_{greg}")])

        await query.edit_message_text(
            "📅 لطفاً تاریخ را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # ------------------ انتخاب ساعت ------------------
    if data.startswith("day_"):
        context.user_data["selected_date"] = data.split("_")[1]
        await query.edit_message_text(
            "⏰ لطفاً ساعت نوبت را انتخاب کنید:",
            reply_markup=time_keyboard()
        )
        return

    if data.startswith("time_"):
        context.user_data["selected_time"] = data.split("_")[1]
        await query.edit_message_text(
            "روش پرداخت را انتخاب کنید:",
            reply_markup=payment_keyboard()
        )
        return

    # ------------------ پرداخت آنلاین ------------------
    if data == "pay_online":
        await query.edit_message_text("💳 پرداخت آنلاین به‌زودی فعال می‌شود.")
        return

    # ------------------ کارت‌به‌کارت ------------------
    if data == "pay_offline":
        await query.edit_message_text(
            card_to_card_text(),
            parse_mode="Markdown"
        )
        return

    # ------------------ پنل مدیریت ------------------
    if data == "admin_panel":
        today = get_appointments_today()
        text = "📋 *نوبت‌های امروز:*\n\n"

        if not today:
            text += "⚠️ هیچ نوبتی ثبت نشده است."
        else:
            for t in today:
                text += f"👨‍⚕️ {t[0]} | 🧴 {t[1]} | ⏰ {t[2]}\n"

        await query.edit_message_text(text, parse_mode="Markdown")
        return



# ------------------ رسید کارت به کارت ------------------

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رسید دریافت شد. نوبت شما تأیید شد 🌸")


# =====================================================
#                WEBHOOK ENDPOINT
# =====================================================

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    update = Update.de_json(data, tg_app.bot)
    asyncio.run(tg_app.process_update(update))
    return "OK", 200


# =====================================================
#                   START BOT
# =====================================================

async def run_bot():
    create_tables()

    if WEBHOOK_URL:
        await tg_app.bot.set_webhook(WEBHOOK_URL)
        print("Webhook OK:", WEBHOOK_URL)

    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(CallbackQueryHandler(handle_callback))
    tg_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("BOT READY ON WEBHOOK...")
    flask_app.run(host="0.0.0.0", port=10000)


if __name__ == "__main__":
    asyncio.run(run_bot())
