from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def rating_keyboard(campaign_id):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐",
                    callback_data=f"rate_{campaign_id}_1"
                ),
                InlineKeyboardButton(
                    text="⭐⭐",
                    callback_data=f"rate_{campaign_id}_2"
                ),
                InlineKeyboardButton(
                    text="⭐⭐⭐",
                    callback_data=f"rate_{campaign_id}_3"
                ),
                InlineKeyboardButton(
                    text="⭐⭐⭐⭐",
                    callback_data=f"rate_{campaign_id}_4"
                ),
                InlineKeyboardButton(
                    text="⭐⭐⭐⭐⭐",
                    callback_data=f"rate_{campaign_id}_5"
                )
            ]
        ]
    )