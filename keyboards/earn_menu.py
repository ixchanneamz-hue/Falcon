from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


def earn_menu():

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="✅ إنجاز مهمة"),
                KeyboardButton(text="📜 سجل مهامي المنجزة")
            ],
            [
                KeyboardButton(text="◀️ العودة للقائمة الرئيسية")
            ]
        ],
        resize_keyboard=True
    )