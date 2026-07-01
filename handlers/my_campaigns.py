from aiogram import Router, F
from aiogram.types import Message

from database.db import SessionLocal
from database.models import Campaign

router = Router()


@router.message(F.text == "📊 حملاتي")
async def my_campaigns(message: Message):

    db = SessionLocal()

    try:

        campaigns = db.query(Campaign).filter(
            Campaign.customer_id == message.from_user.id
        ).all()

        if not campaigns:

            await message.answer(
                "📊 لا توجد لديك حملات حالياً."
            )
            return

        text = "📊 حملاتي\n\n"

        for campaign in campaigns:

            percentage = int(
                (campaign.completed_count * 100)
                / campaign.target_count
            )

            remaining = (
                campaign.target_count
                - campaign.completed_count
            )

            status = "🟢 نشطة"

            if campaign.status == "completed":
                status = "✅ مكتملة"

            text += (
                f"📦 {campaign.package_name}\n\n"
                f"📈 الإنجاز: {campaign.completed_count}/{campaign.target_count}\n"
                f"🎯 المتبقي: {remaining}\n"
                f"📊 نسبة التقدم: {percentage}%\n"
                f"📌 الحالة: {status}\n"
                f"🔗 الرابط:\n{campaign.post_link}\n\n"
                f"━━━━━━━━━━━━━━\n\n"
            )

        await message.answer(text)

    finally:
        db.close()