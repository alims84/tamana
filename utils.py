# ============================
#           UTILS.PY
# ============================

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from config import WHATSAPP_NUMBER, INSTAGRAM_URL, CARD_NUMBER
import jdatetime


# --------------------- منوی اصلی ---------------------

def main_menu_keyboard(is_admin: bool):
    buttons = []

    if is_admin:
        buttons.append([InlineKeyboardButton("⚙️ پنل مدیریت", callback_data="admin_panel")])

    buttons.append([InlineKeyboardButton("📅 رزرو نوبت", callback_data="book")])
    buttons.append([InlineKeyboardButton("👨‍⚕️ پزشکان", callback_data="show_doctors")])
    buttons.append([InlineKeyboardButton("🧴 خدمات", callback_data="show_services")])
    buttons.append([InlineKeyboardButton("ℹ️ درباره کلینیک", callback_data="about")])

    buttons.append([
        InlineKeyboardButton("📞 واتساپ", url=f"https://wa.me/{WHATSAPP_NUMBER}")
    ])

    buttons.append([
        InlineKeyboardButton("📷 اینستاگرام", url=INSTAGRAM_URL)
    ])

    return InlineKeyboardMarkup(buttons)



# --------------------- کیبورد پزشکان ---------------------

def doctor_keyboard(doctors):
    rows = []
    for d in doctors:
        rows.append([InlineKeyboardButton(
            f"{d[1]} — {d[2]}",
            callback_data=f"doc_{d[0]}"
        )])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)



# --------------------- کیبورد خدمات ---------------------

def services_keyboard(items):
    rows = []
    for s in items:
        rows.append([InlineKeyboardButton(s, callback_data=f"service_{s}")])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)



# --------------------- کیبورد زمان ---------------------

def time_keyboard():
    times = [f"{h}:00" for h in range(9, 21)]
    rows = []
    for t in times:
        rows.append([InlineKeyboardButton(t, callback_data=f"time_{t}")])
    rows.append([InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")])
    return InlineKeyboardMarkup(rows)



# --------------------- کیبورد پرداخت ---------------------

def payment_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 پرداخت اینترنتی", callback_data="pay_online")],
        [InlineKeyboardButton("🏦 کارت به کارت", callback_data="pay_offline")],
        [InlineKeyboardButton("⬅ بازگشت", callback_data="back_main")]
    ])



# --------------------- متن کارت‌به‌کارت ---------------------

def card_to_card_text():
    return (
        "💳 *پرداخت کارت‌به‌کارت*\n\n"
        f"شماره کارت:\n`{CARD_NUMBER}`\n\n"
        "لطفاً پس از واریز، تصویر رسید را ارسال کنید. 🌸"
    )



# --------------------- تاریخ جلالی ---------------------

def jalali(dt):
    j = jdatetime.date.fromgregorian(date=dt.date())
    wd = ["دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه","شنبه","یکشنبه"][j.weekday()]
    return f"{j.strftime('%Y/%m/%d')} - {wd}"
