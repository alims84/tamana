from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import WHATSAPP_NUMBER, INSTAGRAM_URL, CARD_NUMBER
import jdatetime


def jalali(dt):
    j = jdatetime.date.fromgregorian(date=dt.date())
    wd = ["دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه","شنبه","یکشنبه"][j.weekday()]
    return f"{j.strftime('%Y/%m/%d')} - {wd}"


def main_menu_keyboard(is_admin):
    buttons = []

    if is_admin:
        buttons.append([InlineKeyboardButton("⚙️ پنل مدیریت", callback_data="admin_panel")])

    buttons.append([InlineKeyboardButton("📅 رزرو نوبت", callback_data="book")])
    buttons.append([InlineKeyboardButton("👨‍⚕️ پزشکان", callback_data="doctors")])
    buttons.append([InlineKeyboardButton("🧴 خدمات", callback_data="services")])
    buttons.append([InlineKeyboardButton("ℹ️ درباره کلینیک", callback_data="about")])
    buttons.append([InlineKeyboardButton("📞 واتساپ", url=f"https://wa.me/{WHATSAPP_NUMBER}")])
    buttons.append([InlineKeyboardButton("📷 اینستاگرام", url=INSTAGRAM_URL)])

    return InlineKeyboardMarkup(buttons)


def doctor_keyboard(doctors):
    rows = []
    for d in doctors:
        rows.append([InlineKeyboardButton(
            f"{d[1]} — {d[2]}", callback_data=f"doc_{d[0]}"
        )])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def services_keyboard(services):
    rows = []
    for s in services:
        rows.append([InlineKeyboardButton(s, callback_data=f"serv_{s}")])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 پرداخت آنلاین", callback_data="pay_online")],
        [InlineKeyboardButton("🏦 کارت‌به‌کارت", callback_data="pay_offline")],
        [InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")]
    ])
