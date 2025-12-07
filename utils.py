
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import jdatetime
from config import WHATSAPP_NUMBER, INSTAGRAM_URL, CARD_NUMBER

def main_menu_keyboard(is_admin):
    buttons = []

    if is_admin:
        buttons.append([InlineKeyboardButton("⚙️ پنل مدیریت", callback_data="admin_panel")])

    buttons.append([InlineKeyboardButton("📅 رزرو نوبت", callback_data="book")])
    buttons.append([InlineKeyboardButton("👨‍⚕️ پزشکان", callback_data="show_doctors")])
    buttons.append([InlineKeyboardButton("🧴 خدمات", callback_data="show_services")])
    buttons.append([InlineKeyboardButton("ℹ️ درباره کلینیک", callback_data="about")])
    buttons.append([InlineKeyboardButton("📞 واتساپ", url=f"https://wa.me/{WHATSAPP_NUMBER}")])
    buttons.append([InlineKeyboardButton("📷 اینستاگرام", url=INSTAGRAM_URL)])

    return InlineKeyboardMarkup(buttons)


def doctor_keyboard(docs):
    rows = []
    for d in docs:
        rows.append([InlineKeyboardButton(f"{d[1]} — {d[2]}", callback_data=f"doc_{d[0]}")])
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
    for h in range(9, 18):
        rows.append([InlineKeyboardButton(f"{h}:00", callback_data=f"time_{h}:00")])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 پرداخت آنلاین", callback_data="pay_online")],
        [InlineKeyboardButton("🏦 کارت‌به‌کارت", callback_data="pay_offline")],
        [InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")]
    ])


def card_to_card_text():
    return (
        "💳 *پرداخت کارت‌به‌کارت*

"
        f"شماره کارت:
`{CARD_NUMBER}`

"
        "بعد از واریز، عکس رسید ارسال شود."
    )


def jalali(dt):
    j = jdatetime.date.fromgregorian(date=dt.date())
    wd = ["دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه","شنبه","یکشنبه"][j.weekday()]
    return f"{j.strftime('%Y/%m/%d')} - {wd}"
