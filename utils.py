# ============================
#          UTILS.PY
# ============================

import jdatetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import WHATSAPP_NUMBER, INSTAGRAM_URL, CARD_NUMBER


def jalali(dt):
    j = jdatetime.date.fromgregorian(date=dt.date())
    wd = ["دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه","شنبه","یکشنبه"][j.weekday()]
    return f"{j.strftime('%Y/%m/%d')} - {wd}"


def main_menu(is_admin):
    buttons = [
        [InlineKeyboardButton("📅 رزرو نوبت", callback_data="book")],
        [InlineKeyboardButton("👨‍⚕️ پزشکان", callback_data="doctors")],
        [InlineKeyboardButton("🧴 خدمات", callback_data="services")],
    ]

    if is_admin:
        buttons.insert(0, [InlineKeyboardButton("⚙️ پنل مدیریت", callback_data="admin_panel")])

    buttons += [
        [InlineKeyboardButton("ℹ️ درباره کلینیک", callback_data="about")],
        [InlineKeyboardButton("📞 واتساپ", url=f"https://wa.me/{WHATSAPP_NUMBER}")],
        [InlineKeyboardButton("📷 اینستاگرام", url=INSTAGRAM_URL)],
    ]

    return InlineKeyboardMarkup(buttons)


def doctor_keyboard(doctors):
    rows = []
    for d in doctors:
        rows.append([InlineKeyboardButton(f"{d[1]} — {d[2]}", callback_data=f"doc_{d[0]}")])
    rows.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def service_keyboard(items):
    rows = []
    for s in items:
        rows.append([InlineKeyboardButton(s, callback_data=f"service_{s}")])
    rows.append([InlineKeyboardButton("⬅️ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 پرداخت اینترنتی", callback_data="pay_online")],
        [InlineKeyboardButton("🏦 کارت به کارت", callback_data="pay_manual")],
        [InlineKeyboardButton("⬅️ بازگشت", callback_data="back_main")],
    ])


def manual_payment_text():
    return (
        "🏦 **پرداخت کارت به کارت**\n\n"
        f"شماره کارت:\n`{CARD_NUMBER}`\n\n"
        "پس از واریز، تصویر رسید را ارسال کنید."
    )
