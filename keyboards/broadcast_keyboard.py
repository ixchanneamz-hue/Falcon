from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def broadcast_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ نشر الآن",
                    callback_data="broadcast_confirm"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ إلغاء",
                    callback_data="broadcast_cancel"
                )
            ]
        ]
    )