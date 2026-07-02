from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from config import ADMIN_ID, CHANNEL_ID, CHANNEL_LINK, CURRENCY
from keyboards.admin_menu import admin_menu
from keyboards.main_menu import main_menu
from keyboards.withdraw_admin import withdraw_admin_keyboard
from keyboards.broadcast_keyboard import broadcast_keyboard
from states.broadcast_states import BroadcastState
from database.db import SessionLocal
from database.models import User, WithdrawRequest, Campaign

router = Router()

FOOTER = f"""
━━━━━━━━━━━━━━
🚀 Falcon Platform
📢 القناة الرسمية
{CHANNEL_LINK}
"""


@router.message(F.text == "💪 لوحة الإدارة")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("💪 لوحة الإدارة", reply_markup=admin_menu())


@router.message(F.text == "📊 الإحصائيات")
async def statistics(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    db = SessionLocal()
    try:
        users_count = db.query(User).count()
        pending_withdraws = db.query(WithdrawRequest).filter(WithdrawRequest.status == "pending").count()
        active_campaigns = db.query(Campaign).filter(Campaign.status == "active").count()
        completed_campaigns = db.query(Campaign).filter(Campaign.status == "completed").count()
        total_balance = sum(user.balance for user in db.query(User).all())

        await message.answer(
            f"📊 الإحصائيات\n"
            f"👥 عدد المستخدمين: {users_count}\n"
            f"🎯 الحملات النشطة: {active_campaigns}\n"
            f"✅ الحملات المكتملة: {completed_campaigns}\n"
            f"💸 طلبات السحب المعلقة: {pending_withdraws}\n"
            f"💰 إجمالي الأرصدة: {total_balance:.3f} {CURRENCY}"
        )
    finally:
        db.close()


@router.message(F.text == "👥 المستخدمون")
async def users_list(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            await message.answer("لا يوجد مستخدمون.")
            return
        text = "👥 قائمة المستخدمين\n"
        for user in users:
            text += (
                f"🆔 {user.telegram_id}\n"
                f"👤 {user.first_name}\n"
                f"💰 الرصيد: {user.balance:.3f} {CURRENCY}\n"
                f"👥 الإحالات: {user.referrals}\n\n"
            )
        await message.answer(text)
    finally:
        db.close()


@router.message(F.text == "📣 نشر إعلان")
async def broadcast_start(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer("📸 أرسل صورة مع النص المرافق للإعلان.")


@router.message(BroadcastState.waiting_for_message, F.photo)
async def receive_broadcast(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    photo_id = message.photo[-1].file_id
    text = message.caption or ""
    await state.update_data(photo_id=photo_id, text=text)
    preview_text = text + FOOTER
    await message.answer_photo(
        photo=photo_id,
        caption="📢 معاينة الإعلان:\n\n" + preview_text,
        reply_markup=broadcast_keyboard()
    )


@router.callback_query(F.data == "broadcast_confirm")
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    data = await state.get_data()
    photo_id = data.get("photo_id")
    text = data.get("text", "")
    final_text = text + FOOTER
    try:
        await callback.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_id, caption=final_text)
        await callback.message.edit_caption(caption="✅ تم نشر الإعلان في القناة بنجاح.")
    except Exception as e:
        await callback.message.answer(f"❌ خطأ أثناء النشر:\n{e}")
    await state.clear()


@router.callback_query(F.data == "broadcast_cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await callback.message.edit_caption(caption="❌ تم إلغاء عملية النشر.")


@router.callback_query(F.data.startswith("withdraw_approve_"))
async def approve_withdraw(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    request_id = int(callback.data.split("_")[2])
    db = SessionLocal()

    try:
        request = db.query(WithdrawRequest).filter(WithdrawRequest.id == request_id).first()
        if not request:
            await callback.answer("الطلب غير موجود", show_alert=True)
            return

        if request.status != "pending":
            await callback.answer("تمت معالجة هذا الطلب مسبقاً", show_alert=True)
            return

        user = db.query(User).filter(User.telegram_id == request.telegram_id).first()
        if not user or user.balance < request.amount:
            await callback.answer("رصيد المستخدم غير كافٍ", show_alert=True)
            return

        request.status = "approved"
        user.balance -= request.amount
        db.commit()

        try:
            await callback.bot.send_message(
                request.telegram_id,
                f"✅ تم قبول طلب السحب رقم #{request.id}\n\n"
                f"💰 المبلغ: {request.amount} {CURRENCY}\n"
                f"📥 عنوان المحفظة: {request.wallet_address}\n\n"
                f"سيتم تحويل المبلغ قريباً."
            )
        except Exception:
            pass

        await callback.message.edit_text(f"✅ تم قبول طلب السحب #{request.id}")
    finally:
        db.close()


@router.message(F.text == "💸 طلبات السحب")
async def withdrawals(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    db = SessionLocal()
    try:
        requests = db.query(WithdrawRequest).filter(WithdrawRequest.status == "pending").all()
        if not requests:
            await message.answer("لا توجد طلبات سحب معلقة.")
            return
        for req in requests:
            await message.answer(
                f"🆔 الطلب: {req.id}\n"
                f"👤 المستخدم: {req.telegram_id}\n"
                f"💰 المبلغ: {req.amount} {CURRENCY}\n"
                f"📥 عنوان المحفظة: {req.wallet_address}\n"
                f"📌 الحالة: {req.status}",
                reply_markup=withdraw_admin_keyboard(req.id)
            )
    finally:
        db.close()


@router.callback_query(F.data.startswith("withdraw_reject_"))
async def reject_withdraw(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return

    request_id = int(callback.data.split("_")[2])
    db = SessionLocal()

    try:
        request = db.query(WithdrawRequest).filter(WithdrawRequest.id == request_id).first()
        if not request:
            await callback.answer("الطلب غير موجود", show_alert=True)
            return

        if request.status != "pending":
            await callback.answer("تمت معالجة هذا الطلب مسبقاً", show_alert=True)
            return

        request.status = "rejected"
        db.commit()

        try:
            await callback.bot.send_message(
                request.telegram_id,
                f"❌ تم رفض طلب السحب رقم #{request.id}\n\n"
                f"يرجى التواصل مع الدعم إذا كنت تعتقد أن هناك خطأ."
            )
        except Exception:
            pass

        await callback.message.edit_text(f"❌ تم رفض طلب السحب #{request.id}")
    finally:
        db.close()


@router.message(F.text == "🏠 رجوع")
async def back_home(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("🏠 القائمة الرئيسية", reply_markup=main_menu(True))


@router.message(Command("reply"))
async def reply_to_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await message.answer("طريقة الاستخدام:\n/reply USER_ID الرسالة")
            return

        user_id = int(parts[1])
        reply_text = parts[2]

        await message.bot.send_message(user_id, f"📩 رد من الدعم الفني\n{reply_text}")
        await message.answer("✅ تم إرسال الرد بنجاح.")
    except Exception as e:
        await message.answer(f"❌ خطأ:\n{e}")
