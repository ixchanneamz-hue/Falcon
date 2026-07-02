from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from config import ADMIN_ID, CHANNEL_ID, CHANNEL_LINK, CURRENCY, REFERRAL_REGISTRATION_BONUS
from keyboards.main_menu import main_menu
from database.db import SessionLocal
from database.models import User
from database.user_service import get_or_create_user

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    if message.from_user.id != ADMIN_ID:
        try:
            member = await message.bot.get_chat_member(
                CHANNEL_ID,
                message.from_user.id
            )

            if member.status in ["left", "kicked"]:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="📢 الانضمام للقناة",
                                url=CHANNEL_LINK
                            )
                        ]
                    ]
                )

                await message.answer(
                    "🚫 يجب الاشتراك في القناة الرسمية أولاً.\n\n"
                    "بعد الاشتراك أرسل /start مرة أخرى.",
                    reply_markup=keyboard
                )
                return

        except Exception:
            await message.answer(
                "❌ تعذر التحقق من الاشتراك.\n"
                "تأكد من إضافة البوت كمشرف في القناة."
            )
            return

    args = message.text.split()
    referrer_id = None

    if len(args) > 1:
        try:
            referrer_id = int(args[1])
        except ValueError:
            pass

    user = get_or_create_user(message.from_user)
    db = SessionLocal()

    try:
        db_user = (
            db.query(User)
            .filter(User.telegram_id == user.telegram_id)
            .first()
        )

        if (
            referrer_id
            and referrer_id != user.telegram_id
            and db_user
            and not db_user.referrer_id
        ):
            referrer = (
                db.query(User)
                .filter(User.telegram_id == referrer_id)
                .first()
            )

            if referrer:
                db_user.referrer_id = referrer_id
                referrer.referrals += 1
                referrer.balance += REFERRAL_REGISTRATION_BONUS
                db.commit()

                try:
                    await message.bot.send_message(
                        referrer_id,
                        "🎉 حصلت على إحالة جديدة!\n"
                        f"💰 تمت إضافة {REFERRAL_REGISTRATION_BONUS:.3f} {CURRENCY} إلى رصيدك."
                    )
                except Exception:
                    pass

        is_admin = message.from_user.id == ADMIN_ID

        await message.answer(
            "🚀 مرحباً بك في Falcon Platform\n\n"
            f"💰 اكسب {CURRENCY} من خلال إنجاز المهام\n"
            "📦 روّج لمنشوراتك عبر الباقات الإعلانية\n"
            "👥 استفد من نظام الإحالات والعمولات\n\n"
            "━━━━━━━━━━━━━━\n\n"
            "اختر الخدمة التي تريدها من القائمة أدناه 👇",
            reply_markup=main_menu(is_admin)
        )

    finally:
        db.close()
