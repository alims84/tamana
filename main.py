# ================================================
#      MAIN.PY — RENDER (PTB 20.x COMPATIBLE)
# ================================================

import os
import asyncio
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
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

# ================================
#         WEBHOOK URL
# ================================

WEBHOOK_URL = os.environ.get("RENDER_EXTERNAL_URL")
if WEBHOOK_URL:
    WEBHOOK_URL = WEBHOOK_URL.rstrip("/") + "/webhook"


# ================================
#         HANDLERS
# ================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = user_id in ADMINS

    await update.message.reply_text(
        f"🌸 خوش آمدید به *{CLINIC_NAME}*\n\n"
        f"🏥 آدرس: {CLINIC_ADDRESS}\n\n"
        "لطفاً یک گزینه را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(is_admin)
    )


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id

    await query.answer()

    if data == "back_main":
        await query.edit_message_text(
            "منوی اصلی:",
            reply_markup=main_menu_keyboard(user_id in ADMINS)
        )
        return

    if data == "show_doctors":
        docs = get_doctors()
        await query.edit_message_text(
            "👨‍⚕️ *لیست پزشکان:*",
            parse_mode="Markdown",
            reply_markup=doctor_keyboard(docs)
        )
        return

    if data == "show_services":
        srv = get_services()
        await query.edit_message_text(
            "🧴 *خدمات کلینیک:*",
            parse_mode="Markdown",
            reply_markup=services_keyboard(srv)
        )
        return

    if data == "book_appointment":
        now = datetime.now()
        buttons = []
        for i in range(7):
            d = now.replace(day=now.day + i)
            greg = d.strftime("%Y-%m-%d")
            j = jalali(d)
            buttons.append([InlineKeyboardButton(j, callback_data=f"day_{greg}")])

        await query.edit_message_text(
            "📅 روز موردنظر را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    if data.startswith("day_"):
        context.user_data["date"] = data.split("_")[1]
        await query.edit_message_text(
            "⏰ انتخاب ساعت:",
            reply_markup=time_keyboard()
        )
        return

    if data.startswith("time_"):
        context.user_data["time"] = data.split("_")[1]
        await query.edit_message_text(
            "روش پرداخت:",
            reply_markup=payment_keyboard()
        )
        return

    if data == "pay_online":
        await query.edit_message_text("💳 پرداخت آنلاین در نسخه بعدی فعال می‌شود.")
        return

    if data == "pay_offline":
        await query.edit_message_text(
            card_to_card_text(),
            parse_mode="Markdown"
        )
        return

    if data == "admin_panel":
        rows = get_appointments_today()
        text = "📋 *نوبت‌های امروز:*\n\n"
        if not rows:
            text += "❌ نوبتی ثبت نشده."
        else:
            for r in rows:
                text += f"👨‍⚕️ {r[0]} | 🧴 {r[1]} | ⏰ {r[2]}\n"

        await query.edit_message_text(text, parse_mode="Markdown")
        return


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("رسید دریافت شد 🌸")


# ================================
#        START WEBHOOK BOT
# ================================

async def main():
    create_tables()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("🚀 Setting Webhook:", WEBHOOK_URL)
    await app.bot.set_webhook(WEBHOOK_URL)

    print("✔ Webhook فعال شد. Listening on port 10000…")

    await app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        url_path="webhook"
    )


if __name__ == "__main__":
    asyncio.run(main())
