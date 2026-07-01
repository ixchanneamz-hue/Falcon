from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


def main_menu(is_admin=False):

    buttons = [
        [
            KeyboardButton(text="💰 كسب المال"),
            KeyboardButton(text="💳 رصيدي")
        ],
        [
            KeyboardButton(text="📊 حملاتي"),
            KeyboardButton(text="📦 شراء الباقات")
        ],
        [
            KeyboardButton(text="👥 الإحالات"),
            KeyboardButton(text="💸 سحب الأرباح")
        ],
        [
            KeyboardButton(text="📞 الدعم الفني")
        ]
    ]

    if is_admin:

        buttons.insert(
            0,
            [
                KeyboardButton(text="💪 لوحة الإدارة")
            ]
        )

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )