import jdatetime
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import WHATSAPP_NUMBER, INSTAGRAM_URL, CARD_NUMBER


def jalali(dt):
    j = jdatetime.date.fromgregorian(date=dt.date())
    wd = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه", "یکشنبه"][j.weekday()]
    return f"{j.strftime('%Y/%m/%d')} - {wd}"


def main_menu_keyboard(is_admin=False):
    rows = []

    if is_admin:
        rows.append([InlineKeyboardButton("⚙️ پنل مدیریت", callback_data="admin_panel")])

    rows += [
        [InlineKeyboardButton("📅 رزرو نوبت", callback_data="book")],
        [InlineKeyboardButton("👨‍⚕️ پزشکان", callback_data="show_doctors")],
        [InlineKeyboardButton("🧴 خدمات", callback_data="show_services")],
        [InlineKeyboardButton("ℹ️ درباره کلینیک", callback_data="about_clinic")],
        [InlineKeyboardButton("📞 واتساپ", url=f"https://wa.me/{WHATSAPP_NUMBER}")],
        [InlineKeyboardButton("📷 اینستاگرام", url=INSTAGRAM_URL)],
    ]

    return InlineKeyboardMarkup(rows)


def doctor_keyboard(doctors):
    rows = []
    for d in doctors:
        rows.append([
            InlineKeyboardButton(f"{d[1]} — {d[2]}", callback_data=f"doc_{d[0]}")
        ])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def services_keyboard(items):
    rows = []
    for s in items:
        rows.append([InlineKeyboardButton(s, callback_data=f"service_{s}")])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def time_keyboard():
    rows = []
    row = []
    for h in range(9, 21):
        row.append(InlineKeyboardButton(f"{h:02d}:00", callback_data=f"time_{h:02d}:00"))
        if len(row) == 4:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(rows)


def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 پرداخت آنلاین", callback_data="pay_online")],
        [InlineKeyboardButton("🏦 کارت به کارت", callback_data="pay_offline")],
        [InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")],
    ])


def card_to_card_text():
    return f"💳 *پرداخت کارت‌به‌کارت*\n\nشماره کارت:\n`{CARD_NUMBER}`\n\nبعد از واریز رسید را ارسال کنید."
