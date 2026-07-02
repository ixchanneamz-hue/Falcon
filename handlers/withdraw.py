from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import CURRENCY, MIN_WITHDRAW, NETWORK
from database.db import SessionLocal
from database.models import User, WithdrawRequest
from states.withdraw_states import WithdrawState

router = Router()


@router.message(F.text.in_([
    "💰 كسب المال",
    "💳 رصيدي",
    "📊 حملاتي",
    "📦 شراء الباقات",
    "👥 الإحالات",
    "📞 الدعم الفني",
    "💪 لوحة الإدارة"
]))
async def cancel_withdraw_state(message: Message, state: FSMContext):
    await state.clear()


@router.message(F.text == "💸 سحب الأرباح")
async def withdraw_start(message: Message, state: FSMContext):
    await state.clear()
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user:
            return

        existing_request = db.query(WithdrawRequest).filter(
            WithdrawRequest.telegram_id == message.from_user.id,
            WithdrawRequest.status == "pending"
        ).first()
        if existing_request:
            await message.answer("⚠️ لديك طلب سحب قيد المراجعة بالفعل.")
            return

        await message.answer(
            f"💸 سحب الأرباح\n\n"
            f"💰 رصيدك الحالي: {user.balance:.3f} {CURRENCY}\n"
            f"📌 الحد الأدنى للسحب: {MIN_WITHDRAW} {CURRENCY}\n"
            f"🌐 الشبكة: {NETWORK}\n\n"
            f"أرسل المبلغ الذي تريد سحبه."
        )
        await state.set_state(WithdrawState.waiting_for_amount)
    finally:
        db.close()


@router.message(WithdrawState.waiting_for_amount)
async def receive_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
    except (TypeError, ValueError):
        await message.answer("❌ أدخل مبلغاً صحيحاً.")
        return

    if amount <= 0:
        await message.answer("❌ يجب أن يكون مبلغ السحب أكبر من صفر.")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user:
            return
        if amount < MIN_WITHDRAW:
            await message.answer(f"❌ الحد الأدنى للسحب هو {MIN_WITHDRAW} {CURRENCY}.")
            return
        if user.balance < amount:
            await message.answer("❌ رصيدك غير كافٍ.")
            return

        await state.update_data(amount=amount)
        await state.set_state(WithdrawState.waiting_for_account)
        await message.answer(
            f"📥 أرسل عنوان محفظة {CURRENCY} الخاصة بك.\n"
            f"🌐 يجب أن تكون على شبكة {NETWORK} فقط."
        )
    finally:
        db.close()


@router.message(WithdrawState.waiting_for_account)
async def receive_account(message: Message, state: FSMContext):
    wallet_address = message.text.strip()
    amount = (await state.get_data()).get("amount")

    if not wallet_address:
        await message.answer("❌ أرسل عنوان محفظة صحيحاً.")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user or user.balance < amount:
            await message.answer("❌ رصيدك غير كافٍ لإتمام طلب السحب.")
            await state.clear()
            return

        request = WithdrawRequest(
            telegram_id=message.from_user.id,
            amount=amount,
            wallet_address=wallet_address,
            status="pending"
        )
        db.add(request)
        db.commit()

        await message.answer(
            f"✅ تم إنشاء طلب السحب بنجاح.\n\n"
            f"💰 المبلغ: {amount} {CURRENCY}\n"
            f"🌐 الشبكة: {NETWORK}\n"
            f"📥 عنوان المحفظة:\n{wallet_address}\n\n"
            f"📌 الحالة: قيد المراجعة."
        )
    finally:
        db.close()

    await state.clear()
