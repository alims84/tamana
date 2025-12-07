# ============================
#           MAIN.PY
# ============================

import logging
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, ContextTypes, CommandHandler,
    CallbackQueryHandler, MessageHandler, filters
)
import uvicorn
from datetime import datetime, timedelta

from config import BOT_TOKEN, ADMINS, WEBHOOK_URL
from database import (
    create_tables, get_doctors, get_services,
    create_appointment, get_appointments_today
)
from utils import (
    main_menu, doctor_keyboard, service_keyboard,
    payment_keyboard, jalali, manual_payment_text
)

logging.basicConfig(level=logging.INFO)

# FastAPI
app = FastAPI()

# Telegram Application
tg = Application.builder().token(BOT_TOKEN).build()


# ============================
#       Handlers
# ============================

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_admin = user.id in ADMINS
    await update.message.reply_text(
        f"سلام {user.first_name} عزیز 🌸\n\nبه ربات کلینیک تمارا خوش آمدید.",
        reply_markup=main_menu(is_admin)
    )


async def show_doctors(update, ctx):
    q = update.callback_query
    await q.answer()
    doctors = get_doctors()
    await q.message.edit_text("👨‍⚕️ پزشکان:", reply_markup=doctor_keyboard(doctors))


async def show_services(update, ctx):
    q = update.callback_query
    await q.answer()
    services = get_services()
    await q.message.edit_text("🧴 خدمات:", reply_markup=service_keyboard(services))


async def about(update, ctx):
    msg = (
        "ℹ️ **درباره کلینیک تمارا**\n\n"
        "آدرس: دماوند - خیابان بهشتی\n"
        "تجهیزات پیشرفته و کادر مجرب 🌸"
    )
    if update.callback_query:
        q = update.callback_query
        await q.answer()
        await q.message.edit_text(msg)
    else:
        await update.message.reply_text(msg)


# --- رزرو نوبت ---
async def book(update, ctx):
    q = update.callback_query
    await q.answer()
    doctors = get_doctors()
    await q.message.edit_text("👨‍⚕️ پزشک را انتخاب کنید:", reply_markup=doctor_keyboard(doctors))


async def select_doctor(update, ctx):
    q = update.callback_query
    await q.answer()
    doc_id = q.data.replace("doc_", "")
    ctx.user_data["doctor"] = doc_id

    services = get_services()
    await q.message.edit_text("🔹 خدمت را انتخاب کنید:", reply_markup=service_keyboard(services))


async def select_service(update, ctx):
    q = update.callback_query
    await q.answer()
    srv = q.data.replace("service_", "")
    ctx.user_data["service"] = srv

    now = datetime.now()
    rows = []
    for i in range(10):
        d = now + timedelta(days=i)
        rows.append([InlineKeyboardButton(jalali(d), callback_data=f"date_{d.strftime('%Y-%m-%d')}")])
    rows.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="back_main")])

    await q.message.edit_text("📅 تاریخ را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(rows))


async def select_date(update, ctx):
    q = update.callback_query
    await q.answer()
    date_g = q.data.replace("date_", "")
    dt = datetime.strptime(date_g, "%Y-%m-%d")

    ctx.user_data["date_greg"] = date_g
    ctx.user_data["date_jalali"] = jalali(dt)

    times = []
    row = []
    for h in range(9, 21):
        row.append(InlineKeyboardButton(f"{h}:00", callback_data=f"time_{h}"))
        if len(row) == 4:
            times.append(row)
            row = []
    if row:
        times.append(row)

    await q.message.edit_text("⏰ ساعت را انتخاب کنید:", reply_markup=InlineKeyboardMarkup(times))


async def select_time(update, ctx):
    q = update.callback_query
    await q.answer()
    time_ = q.data.replace("time_", "")
    ctx.user_data["time"] = f"{time_}:00"

    user = q.from_user
    doctor = get_doctors()[int(ctx.user_data["doctor"]) - 1]  # mapping
    service = ctx.user_data["service"]

    create_appointment({
        "user_id": user.id,
        "full_name": user.full_name,
        "doctor": doctor[1] + " — " + doctor[2],
        "service": service,
        "date_greg": ctx.user_data["date_greg"],
        "date_jalali": ctx.user_data["date_jalali"],
        "time": ctx.user_data["time"]
    })

    await q.message.edit_text(
        "🎉 **نوبت شما ثبت شد!**\n\n"
        f"👨‍⚕️ پزشک: {doctor[1]}\n"
        f"🔸 خدمت: {service}\n"
        f"📅 تاریخ: {ctx.user_data['date_jalali']}\n"
        f"⏰ ساعت: {ctx.user_data['time']}\n\n"
        "لطفاً روش پرداخت را انتخاب کنید:",
        reply_markup=payment_keyboard()
    )


# --- پرداخت ---
async def pay_manual(update, ctx):
    q = update.callback_query
    await q.answer()
    await q.message.edit_text(manual_payment_text())


async def pay_online(update, ctx):
    q = update.callback_query
    await q.answer()
    await q.message.edit_text(
        "درگاه اینترنتی NextPay به‌زودی فعال می‌شود 🔄"
    )


# --- پنل مدیریت ---
async def admin_panel(update, ctx):
    q = update.callback_query
    await q.answer()

    if q.from_user.id not in ADMINS:
        return await q.message.edit_text("⛔ شما ادمین نیستید.")

    today_apps = get_appointments_today()
    txt = "📋 نوبت‌های امروز:\n\n"
    if not today_apps:
        txt += "هیچ نوبتی ثبت نشده."
    else:
        for a in today_apps:
            txt += f"- {a[3]} | {a[4]} | {a[6]} | {a[7]}\n"

    await q.message.edit_text(txt)


# ============================
#        FastAPI Webhook
# ============================

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, tg.bot)
    await tg.process_update(update)
    return {"ok": True}


@app.get("/")
def home():
    return {"status": "OK", "bot": "Tamara Clinic Bot"}


# ============================
#         Startup
# ============================

async def run_bot():
    create_tables()

    await tg.initialize()
    await tg.bot.set_webhook(WEBHOOK_URL)
    await tg.start()
    print("Bot is running via Webhook...")


import asyncio
asyncio.get_event_loop().run_until_complete(run_bot())
