from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def withdraw_admin_keyboard(withdraw_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ قبول",
                    callback_data=f"withdraw_approve_{withdraw_id}"
                ),
                InlineKeyboardButton(
                    text="❌ رفض",
                    callback_data=f"withdraw_reject_{withdraw_id}"
                )
            ]
        ]
    )
