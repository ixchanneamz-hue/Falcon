from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton

def withdraw_admin_keyboard(request_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ قبول السحب",
                    callback_data=f"withdraw_approve_{request_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ رفض السحب",
                    callback_data=f"withdraw_reject_{request_id}"
                )
            ]
        ]
    )