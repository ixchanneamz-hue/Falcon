from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def withdraw_admin_keyboard(
    withdraw_id: int
):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ قبول",
                    callback_data=f"approve_withdraw_{withdraw_id}"
                ),
                InlineKeyboardButton(
                    text="❌ رفض",
                    callback_data=f"reject_withdraw_{withdraw_id}"
                )
            ]
        ]
    )