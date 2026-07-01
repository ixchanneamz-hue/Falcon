from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


def admin_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 الإحصائيات"),
                KeyboardButton(text="💸 طلبات السحب")
            ],
            [
                KeyboardButton(text="🎯 إدارة الحملات"),
                KeyboardButton(text="👥 المستخدمون")
            ],
            [
                KeyboardButton(text="📣 نشر إعلان")
            ],
            [
                KeyboardButton(text="🏠 رجوع")
            ]
        ],
        resize_keyboard=True
    )