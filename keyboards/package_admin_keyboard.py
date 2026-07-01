from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def package_admin_keyboard(order_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ قبول الطلب",
                    callback_data=f"approve_package_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ رفض الطلب",
                    callback_data=f"reject_package_{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 حذف الطلب",
                    callback_data=f"delete_package_{order_id}"
                )
            ]
        ]
    )