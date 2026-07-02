import time

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID, CURRENCY, REFERRAL_COMMISSION_RATE
from keyboards.earn_menu import earn_menu
from keyboards.main_menu import main_menu
from keyboards.rating_keyboard import rating_keyboard
from database.db import SessionLocal
from database.models import (
    Campaign,
    CampaignParticipant,
    CampaignComment,
    User,
    ReferralEarning
)
from states.task_states import UserTaskState

router = Router()


@router.message(F.text == "💰 كسب المال")
async def earn_money(message: Message):
    await message.answer(
        "💰 مرحباً بك في قسم كسب المال\n"
        "اربح المال من الحملات المتاحة.",
        reply_markup=earn_menu()
    )


@router.message(F.text == "✅ إنجاز مهمة")
async def task_handler(message: Message, state: FSMContext):
    db = SessionLocal()
    try:
        campaigns = db.query(Campaign).filter(Campaign.status == "active").all()
        if not campaigns:
            await message.answer("📋 لا توجد حملات متاحة حالياً.")
            return
        user_id = message.from_user.id
        for campaign in campaigns:
            completed = db.query(CampaignParticipant).filter(
                CampaignParticipant.telegram_id == user_id,
                CampaignParticipant.campaign_id == campaign.id
            ).first()
            if completed:
                continue
            if campaign.completed_count >= campaign.target_count:
                continue
            await state.update_data(
                campaign_id=campaign.id,
                start_time=time.time()
            )
            await state.set_state(UserTaskState.waiting_for_comment)

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="🔗 فتح المنشور",
                            url=campaign.post_link
                        )
                    ]
                ]
            )

            await message.answer(
                f"🎥 مهمة جديدة\n"
                f"💰 المكافأة: {campaign.reward:.3f} {CURRENCY}\n"
                f"📋 التعليمات:\n"
                f"• اضغط على زر فتح المنشور.\n"
                f"• شاهد المحتوى لمدة 30 ثانية.\n"
                f"• ارجع إلى البوت.\n"
                f"• اكتب تعليقاً من 3 كلمات على الأقل.\n\n"
                f"⏳ لن تتمكن من إرسال التعليق قبل مرور 30 ثانية.",
                reply_markup=keyboard
            )
            return
        await message.answer("✅ لقد أنجزت جميع الحملات المتاحة.")
    finally:
        db.close()


@router.message(UserTaskState.waiting_for_comment)
async def save_comment(message: Message, state: FSMContext):
    comment = message.text.strip()
    data = await state.get_data()
    start_time = data.get("start_time", 0)

    if time.time() - start_time < 30:
        remaining = max(0, int(30 - (time.time() - start_time)))
        await message.answer(f"⏳ يرجى الانتظار {remaining} ثانية قبل إرسال التعليق.")
        return

    if len(comment.split()) < 3:
        await message.answer("❌ يجب أن يحتوي التعليق على 3 كلمات على الأقل.")
        return

    await state.update_data(comment=comment)
    campaign_id = data.get("campaign_id")
    await state.set_state(UserTaskState.waiting_for_rating)
    await message.answer("⭐ قم بتقييم الفيديو:", reply_markup=rating_keyboard(campaign_id))


@router.callback_query(F.data.startswith("rate_"))
async def save_rating(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    campaign_id = int(callback.data.split("_")[1])
    rating = int(callback.data.split("_")[2])
    comment = data.get("comment")
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign or campaign.status != "active":
            await callback.message.answer("❌ الحملة غير متاحة حالياً.")
            await state.clear()
            return

        if campaign.completed_count >= campaign.target_count:
            campaign.status = "completed"
            db.commit()
            await callback.message.answer("❌ اكتملت هذه الحملة بالفعل.")
            await state.clear()
            return

        user = db.query(User).filter(User.telegram_id == callback.from_user.id).first()
        if not user:
            await state.clear()
            return

        already_done = db.query(CampaignParticipant).filter(
            CampaignParticipant.telegram_id == callback.from_user.id,
            CampaignParticipant.campaign_id == campaign.id
        ).first()
        if already_done:
            await callback.answer("لقد أنجزت هذه الحملة مسبقاً")
            await state.clear()
            return

        feedback = CampaignComment(
            campaign_id=campaign.id,
            telegram_id=callback.from_user.id,
            comment=comment,
            rating=rating
        )
        db.add(feedback)
        db.add(CampaignParticipant(campaign_id=campaign.id, telegram_id=callback.from_user.id))

        campaign.completed_count += 1
        user.balance += campaign.reward

        if user.referrer_id:
            completed_tasks = db.query(CampaignParticipant).filter(
                CampaignParticipant.telegram_id == user.telegram_id
            ).count()

            if completed_tasks >= 5:
                referrer = db.query(User).filter(User.telegram_id == user.referrer_id).first()
                if referrer:
                    commission = campaign.reward * REFERRAL_COMMISSION_RATE
                    referrer.balance += commission
                    db.add(ReferralEarning(
                        referrer_id=referrer.telegram_id,
                        referred_id=user.telegram_id,
                        amount=commission,
                        status="approved"
                    ))
                    try:
                        await callback.bot.send_message(
                            referrer.telegram_id,
                            f"🎉 حصلت على عمولة إحالة\n"
                            f"💰 القيمة: {commission:.3f} {CURRENCY}\n"
                            f"👤 من المستخدم: {user.first_name}"
                        )
                    except Exception:
                        pass

        if campaign.completed_count >= campaign.target_count:
            campaign.status = "completed"
            try:
                await callback.bot.send_message(
                    campaign.customer_id,
                    f"🎉 تم الانتهاء من حملتك بنجاح!\n\n"
                    f"📦 {campaign.package_name}\n"
                    f"✅ {campaign.completed_count}/{campaign.target_count}\n\n"
                    f"🚀 شكراً لاستخدام منصة Falcon"
                )
            except Exception:
                pass

        db.commit()
        await callback.message.edit_text(
            f"✅ تم حفظ تعليقك وتقييمك.\n\n"
            f"⭐ التقييم: {rating}/5\n"
            f"💰 تمت إضافة {campaign.reward:.3f} {CURRENCY} إلى رصيدك."
        )
    finally:
        db.close()
    await state.clear()


@router.message(F.text == "📜 سجل مهامي المنجزة")
async def task_history(message: Message):
    db = SessionLocal()
    try:
        completed = db.query(CampaignParticipant).filter(
            CampaignParticipant.telegram_id == message.from_user.id
        ).all()
        if not completed:
            await message.answer("📜 لا توجد حملات منجزة بعد.")
            return
        text = "📜 الحملات المنجزة\n"
        for item in completed:
            campaign = db.query(Campaign).filter(Campaign.id == item.campaign_id).first()
            if campaign:
                text += f"🎥 {campaign.package_name}\n💰 {campaign.reward:.3f} {CURRENCY}\n"
        await message.answer(text)
    finally:
        db.close()


@router.message(F.text == "◀️ العودة للقائمة الرئيسية")
async def back_home(message: Message):
    is_admin = message.from_user.id == ADMIN_ID
    await message.answer("🏠 القائمة الرئيسية", reply_markup=main_menu(is_admin))
