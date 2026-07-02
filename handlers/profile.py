from aiogram import Router, F
from aiogram.types import Message

from config import CURRENCY
from database.db import SessionLocal
from database.models import (
    User,
    CampaignParticipant
)

router = Router()


@router.message(F.text == "💳 رصيدي")
async def my_balance(message: Message):
    db = SessionLocal()

    try:
        user = db.query(User).filter(
            User.telegram_id == message.from_user.id
        ).first()

        if not user:
            await message.answer("❌ المستخدم غير موجود.")
            return

        completed_campaigns = db.query(CampaignParticipant).filter(
            CampaignParticipant.telegram_id == message.from_user.id
        ).count()

        await message.answer(
            f"💳 معلومات الحساب\n\n"
            f"💰 الرصيد الحالي: {user.balance:.3f} {CURRENCY}\n"
            f"👥 عدد الإحالات: {user.referrals}\n"
            f"🎥 عدد الحملات المنجزة: {completed_campaigns}"
        )

    finally:
        db.close()
