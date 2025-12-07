# ============================
#         UTILS.PY
# ============================

import jdatetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import WHATSAPP_NUMBER, INSTAGRAM_URL, CARD_NUMBER


# ------------ MAIN MENU ------------

def main_menu_keyboard(is_admin=False):
    btn = []

    if is_admin:
        btn.append([InlineKeyboardButton("⚙️ پنل مدیریت", callback_data="admin_panel")])

    btn.append([InlineKeyboardButton("📅 رزرو نوبت", callback_data="book")])
    btn.append([InlineKeyboardButton("👨‍⚕️ پزشکان", callback_data="doctors")])
    btn.append([InlineKeyboardButton("🧴 خدمات", callback_data="services")])
    btn.append([InlineKeyboardButton("ℹ️ درباره کلینیک", callback_data="about")])
    btn.append([InlineKeyboardButton("📞 واتساپ", url=f"https://wa.me/{WHATSAPP_NUMBER}")])
    btn.append([InlineKeyboardButton("📷 اینستاگرام", url=INSTAGRAM_URL)])

    return InlineKeyboardMarkup(btn)


# ------------ DOCTORS ------------

def doctors_keyboard(doctors):
    rows = []
    for d in doctors:
        rows.append([
            InlineKeyboardButton(f"{d[1]} — {d[2]}", callback_data=f"doc_{d[0]}")
        ])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


# ------------ SERVICES ------------

def services_keyboard(items):
    rows = []
    for s in items:
        rows.append([InlineKeyboardButton(s, callback_data=f"service_{s}")])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)


# ------------ PAYMENT ------------

def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 پرداخت اینترنتی", callback_data="pay_online")],
        [InlineKeyboardButton("🏦 کارت‌به‌کارت", callback_data="pay_manual")],
        [InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")]
    ])


def card_to_card_text():
    return (
        "💳 **پرداخت کارت‌به‌کارت**\n\n"
        f"شماره کارت:\n`{CARD_NUMBER}`\n\n"
        "پس از واریز، لطفاً رسید را ارسال کنید."
    )


# -------- تاریخ شمسی --------

def to_jalali(date):
    j = jdatetime.date.fromgregorian(date=date)
    weekday = ["دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه","شنبه","یکشنبه"][j.weekday()]
    return f"{j.strftime('%Y/%m/%d')} - {weekday}"
