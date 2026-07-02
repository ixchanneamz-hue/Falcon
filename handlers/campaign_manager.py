from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import ADMIN_ID, CURRENCY
from database.db import SessionLocal
from database.models import Campaign
from keyboards.campaign_admin_keyboard import campaign_admin_keyboard

router = Router()


@router.message(F.text == "🎯 إدارة الحملات")
async def manage_campaigns(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    db = SessionLocal()

    try:
        campaigns = db.query(Campaign).order_by(Campaign.id.desc()).all()

        if not campaigns:
            await message.answer("📭 لا توجد حملات حالياً.")
            return

        for campaign in campaigns:
            status = "🟢 نشطة"
            if campaign.status == "completed":
                status = "✅ مكتملة"
            elif campaign.status == "paused":
                status = "⏸ متوقفة"

            await message.answer(
                f"🆔 {campaign.id}\n"
                f"📦 {campaign.package_name}\n"
                f"👤 {campaign.customer_id}\n"
                f"📈 {campaign.completed_count}/{campaign.target_count}\n"
                f"💰 {campaign.reward:.3f} {CURRENCY}\n"
                f"📌 {status}",
                reply_markup=campaign_admin_keyboard(campaign.id)
            )

    finally:
        db.close()


@router.callback_query(F.data.startswith("pause_campaign_"))
async def pause_campaign(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    campaign_id = int(callback.data.split("_")[2])
    db = SessionLocal()

    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            await callback.answer("الحملة غير موجودة", show_alert=True)
            return

        campaign.status = "paused"
        db.commit()

        await callback.message.edit_text(f"⏸ تم إيقاف الحملة #{campaign.id}")
    finally:
        db.close()


@router.callback_query(F.data.startswith("delete_campaign_"))
async def delete_campaign(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    campaign_id = int(callback.data.split("_")[2])
    db = SessionLocal()

    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            await callback.answer("الحملة غير موجودة", show_alert=True)
            return

        db.delete(campaign)
        db.commit()

        await callback.message.edit_text(f"🗑 تم حذف الحملة #{campaign_id}")
    finally:
        db.close()
