# ================================================
#             MAIN.PY — RENDER WEBHOOK
# ================================================

import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
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
    get_appointments_today
)

from datetime import datetime


WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")
if WEBHOOK_URL:
    WEBHOOK_URL = WEBHOOK_URL.rstrip("/") + "/webhook"


# ==========================================================
#                      BOT HANDLERS
# ==========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id in ADMINS

    await update.message.reply_text(
        f"🌸 خوش آمدید به *{CLINIC_NAME}*\n\n"
        f"🏥 آدرس: {CLINIC_ADDRESS}\n\n"
        "لطفاً یک گزینه را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(is_admin),
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
            parse_mode="Markdown",
            reply_markup=doctor_keyboard(docs)
        )
        return

    # خدمات
    if data == "show_services":
        srv = get_services()
        await query.edit_message_text(
            "🧴 *خدمات کلینیک:*",
            parse_mode="Markdown",
            reply_markup=services_keyboard(srv)
        )
        return

    # شروع رزرو
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

    # انتخاب تاریخ
    if data.startswith("day_"):
        context.user_data["date"] = data.split("_")[1]
        await query.edit_message_text(
            "⏰ انتخاب ساعت:",
            reply_markup=time_keyboard()
        )
        return

    # انتخاب ساعت
    if data.startswith("time_"):
        context.user_data["time"] = data.split("_")[1]
        await query.edit_message_text(
            "روش پرداخت:",
            reply_markup=payment_keyboard()
        )
        return

    # پرداخت آنلاین
    if data == "pay_online":
        await query.edit_message_text("💳 در نسخه بعدی فعال می‌شود.")
        return

    if data == "pay_offline":
        await query.edit_message_text(
            card_to_card_text(), parse_mode="Markdown"
        )
        return

    # پنل مدیریت
    if data == "admin_panel":
        today = get_appointments_today()
        txt = "📋 *نوبت‌های امروز:*\n\n"
        if not today:
            txt += "❌ نوبتی ثبت نشده"

        else:
            for t in today:
                txt += f"👨‍⚕️ {t[0]} | 🧴 {t[1]} | ⏰ {t[2]}\n"

        await query.edit_message_text(txt, parse_mode="Markdown")
        return


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رسید دریافت شد 🌸")


# ==========================================================
#                      RUN BOT
# ==========================================================

async def setup():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .webhook_url(WEBHOOK_URL)
        .build()
    )

    create_tables()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    print("✔ Webhook فعال شد:", WEBHOOK_URL)
    await app.initialize()
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path="webhook",
        webhook_url=WEBHOOK_URL,
    )
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(setup())
