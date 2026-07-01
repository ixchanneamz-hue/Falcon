from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def campaign_admin_keyboard(campaign_id):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⏸ إيقاف الحملة",
                    callback_data=f"pause_campaign_{campaign_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 حذف الحملة",
                    callback_data=f"delete_campaign_{campaign_id}"
                )
            ]
        ]
    )