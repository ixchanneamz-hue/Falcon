from aiogram import Router, F
from aiogram.types import Message

from config import BOT_USERNAME, CURRENCY, REFERRAL_REGISTRATION_BONUS
from database.db import SessionLocal
from database.models import User, ReferralEarning

router = Router()


@router.message(F.text == "👥 الإحالات")
async def referrals_handler(message: Message):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.telegram_id == message.from_user.id
        ).first()

        if not user:
            await message.answer("❌ المستخدم غير موجود.")
            return

        referral_link = f"https://t.me/{BOT_USERNAME}?start={message.from_user.id}"

        referral_commissions = db.query(ReferralEarning).filter(
            ReferralEarning.referrer_id == user.telegram_id
        ).all()

        total_commissions = sum(item.amount for item in referral_commissions)
        total_referrals = user.referrals
        registration_bonus = total_referrals * REFERRAL_REGISTRATION_BONUS
        total_referral_earnings = registration_bonus + total_commissions

        await message.answer(
            f"👥 نظام الإحالات\n\n"
            f"🔗 رابط الدعوة:\n"
            f"{referral_link}\n\n"
            f"👤 عدد المدعوين: {total_referrals}\n"
            f"🎁 أرباح التسجيل: {registration_bonus:.3f} {CURRENCY}\n"
            f"💰 عمولات الإحالات: {total_commissions:.3f} {CURRENCY}\n"
            f"🏆 إجمالي أرباح الإحالات: {total_referral_earnings:.3f} {CURRENCY}"
        )

    finally:
        db.close()
