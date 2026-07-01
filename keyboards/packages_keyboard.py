from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


def packages_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🥉 البرونزية",
                    callback_data="package_bronze"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🥈 الفضية",
                    callback_data="package_silver"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🥇 الذهبية",
                    callback_data="package_gold"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💎 الماسية",
                    callback_data="package_diamond"
                )
            ]
        ]
    )