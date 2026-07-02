from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext

from config import (
    ADMIN_ID,
    BOT_USERNAME,
    BINANCE_WALLET,
    CAMPAIGN_REWARD,
    CHANNEL_ID,
    CURRENCY,
    NETWORK,
    require_config,
)
from database.db import SessionLocal
from database.models import PackageOrder, Campaign
from keyboards.packages_keyboard import packages_keyboard
from keyboards.package_admin_keyboard import package_admin_keyboard
from states.package_states import PackageOrderState

router = Router()

PACKAGE_TARGETS = {
    "الفضية": 1000,
    "الذهبية": 2000,
    "الماسية": 4000,
}


@router.message(F.text == "📦 شراء الباقات")
async def packages_menu(message: Message):
    await message.answer(
        "📦 الباقات المتاحة\n"
        "اختر الباقة المناسبة من الأزرار التالية 👇",
        reply_markup=packages_keyboard()
    )


@router.callback_query(F.data == "package_bronze")
async def bronze_package(callback: CallbackQuery, state: FSMContext):
    await state.update_data(package_name="🥉 الباقة البرونزية", package_price=5)
    await state.set_state(PackageOrderState.waiting_for_post_link)
    await callback.message.answer(
        "🥉 الباقة البرونزية\n\n"
        "👥 حتى 500 منفذ\n"
        "💬 تعليقات حقيقية\n"
        "⏱️ مشاهدة لا تقل عن 30 ثانية\n\n"
        f"💰 السعر: 5 {CURRENCY}\n\n"
        "📎 أرسل رابط المنشور."
    )


@router.callback_query(F.data == "package_silver")
async def silver_package(callback: CallbackQuery, state: FSMContext):
    await state.update_data(package_name="🥈 الباقة الفضية", package_price=10)
    await state.set_state(PackageOrderState.waiting_for_post_link)
    await callback.message.answer(
        "🥈 الباقة الفضية\n\n"
        "👥 حتى 1000 منفذ\n"
        "💬 تعليقات حقيقية\n"
        "⏱️ مشاهدة لا تقل عن 30 ثانية\n\n"
        f"💰 السعر: 10 {CURRENCY}\n\n"
        "📎 أرسل رابط المنشور."
    )


@router.callback_query(F.data == "package_gold")
async def gold_package(callback: CallbackQuery, state: FSMContext):
    await state.update_data(package_name="🥇 الباقة الذهبية", package_price=20)
    await state.set_state(PackageOrderState.waiting_for_post_link)
    await callback.message.answer(
        "🥇 الباقة الذهبية\n\n"
        "👥 حتى 2000 منفذ\n"
        "💬 تعليقات حقيقية\n"
        "⏱️ مشاهدة لا تقل عن 30 ثانية\n\n"
        f"💰 السعر: 20 {CURRENCY}\n\n"
        "📎 أرسل رابط المنشور."
    )


@router.callback_query(F.data == "package_diamond")
async def diamond_package(callback: CallbackQuery, state: FSMContext):
    await state.update_data(package_name="💎 الباقة الماسية", package_price=40)
    await state.set_state(PackageOrderState.waiting_for_post_link)
    await callback.message.answer(
        "💎 الباقة الماسية\n\n"
        "👥 حتى 4000 منفذ\n"
        "💬 تعليقات حقيقية\n"
        "⏱️ مشاهدة لا تقل عن 30 ثانية\n\n"
        f"💰 السعر: 40 {CURRENCY}\n\n"
        "📎 أرسل رابط المنشور."
    )


@router.message(PackageOrderState.waiting_for_post_link)
async def receive_post_link(message: Message, state: FSMContext):
    post_link = message.text.strip()
    if not post_link:
        await message.answer("❌ أرسل رابط منشور صحيحاً.")
        return

    await state.update_data(post_link=post_link)
    data = await state.get_data()
    await state.set_state(PackageOrderState.waiting_for_payment_image)

    await message.answer(
        f"💳 الدفع عبر Binance\n\n"
        f"💰 العملة: {CURRENCY}\n"
        f"🌐 الشبكة: {NETWORK}\n\n"
        f"💰 المبلغ المطلوب: {data['package_price']} {CURRENCY}\n\n"
        f"📥 عنوان المحفظة:\n"
        f"{require_config(BINANCE_WALLET, 'BINANCE_WALLET')}\n\n"
        f"📸 بعد التحويل أرسل صورة إثبات الدفع."
    )


@router.message(PackageOrderState.waiting_for_payment_image, F.photo)
async def receive_payment_image(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id
    db = SessionLocal()

    try:
        order = PackageOrder(
            telegram_id=message.from_user.id,
            package_name=data["package_name"],
            package_price=data["package_price"],
            post_link=data["post_link"],
            payment_image=photo_id,
            status="pending"
        )

        db.add(order)
        db.commit()
        db.refresh(order)

        await message.bot.send_photo(
            ADMIN_ID,
            photo=photo_id,
            caption=(
                f"📦 طلب باقة جديد\n\n"
                f"🆔 رقم الطلب: {order.id}\n"
                f"👤 المستخدم: {message.from_user.id}\n"
                f"📦 الباقة: {order.package_name}\n"
                f"💰 السعر: {order.package_price} {CURRENCY}\n\n"
                f"🔗 الرابط:\n{order.post_link}"
            ),
            reply_markup=package_admin_keyboard(order.id)
        )

        await message.answer(
            "✅ تم إرسال طلبك بنجاح.\n\n"
            "سيتم مراجعته من طرف الإدارة."
        )

    finally:
        db.close()

    await state.clear()


@router.callback_query(F.data.startswith("approve_package_"))
async def accept_package(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        return

    order_id = int(callback.data.split("_")[2])
    db = SessionLocal()

    try:
        order = db.query(PackageOrder).filter(PackageOrder.id == order_id).first()

        if not order:
            await callback.answer("الطلب غير موجود", show_alert=True)
            return

        if order.status == "approved":
            await callback.answer("تمت الموافقة على هذا الطلب مسبقاً", show_alert=True)
            return

        if order.status == "rejected":
            await callback.answer("تم رفض هذا الطلب مسبقاً", show_alert=True)
            return

        existing_campaign = db.query(Campaign).filter(Campaign.order_id == order.id).first()
        if existing_campaign:
            await callback.answer("توجد حملة مرتبطة بهذا الطلب", show_alert=True)
            return

        order.status = "approved"
        target_count = 500
        for package_key, package_target in PACKAGE_TARGETS.items():
            if package_key in order.package_name:
                target_count = package_target
                break

        campaign = Campaign(
            order_id=order.id,
            customer_id=order.telegram_id,
            package_name=order.package_name,
            post_link=order.post_link,
            target_count=target_count,
            completed_count=0,
            reward=CAMPAIGN_REWARD,
            status="active"
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        try:
            await bot.send_message(
                order.telegram_id,
                f"🎉 تم قبول طلبك بنجاح.\n\n"
                f"📦 {order.package_name}\n"
                f"🎯 عدد المنفذين: {target_count}\n\n"
                f"🚀 بدأت الحملة الآن."
            )
        except Exception:
            pass

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="💰 ابدأ المهمة",
                        url=f"https://t.me/{BOT_USERNAME}"
                    )
                ]
            ]
        )

        try:
            await bot.send_message(
                CHANNEL_ID,
                f"📢 حملة جديدة متاحة\n\n"
                f"💰 المكافأة: {CAMPAIGN_REWARD:.3f} {CURRENCY}\n\n"
                f"👇 اضغط على الزر التالي لبدء التنفيذ.",
                reply_markup=keyboard
            )
        except Exception as e:
            print(e)

        await callback.message.edit_caption(
            caption=(
                f"✅ تمت الموافقة على الطلب\n\n"
                f"📦 {order.package_name}\n"
                f"🎯 عدد المنفذين: {target_count}"
            )
        )
        await callback.answer("تم قبول الطلب")

    finally:
        db.close()


@router.callback_query(F.data.startswith("reject_package_"))
async def reject_package(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        return

    order_id = int(callback.data.split("_")[2])
    db = SessionLocal()

    try:
        order = db.query(PackageOrder).filter(PackageOrder.id == order_id).first()

        if not order:
            await callback.answer("الطلب غير موجود", show_alert=True)
            return

        if order.status != "pending":
            await callback.answer("تمت معالجة الطلب مسبقاً", show_alert=True)
            return

        order.status = "rejected"
        db.commit()

        try:
            await bot.send_message(
                order.telegram_id,
                "❌ تم رفض طلب الباقة.\n\n"
                "يرجى التواصل مع الدعم."
            )
        except Exception:
            pass

        await callback.message.edit_caption(caption=f"❌ تم رفض الطلب #{order.id}")
        await callback.answer("تم رفض الطلب")

    finally:
        db.close()


@router.callback_query(F.data.startswith("delete_package_"))
async def delete_package(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id != ADMIN_ID:
        return

    order_id = int(callback.data.split("_")[2])
    db = SessionLocal()

    try:
        order = db.query(PackageOrder).filter(PackageOrder.id == order_id).first()

        if not order:
            await callback.answer("الطلب غير موجود", show_alert=True)
            return

        try:
            await bot.send_message(
                order.telegram_id,
                "🗑 تم حذف طلب الباقة من طرف الإدارة."
            )
        except Exception:
            pass

        db.delete(order)
        db.commit()

        await callback.message.edit_caption(caption=f"🗑 تم حذف الطلب #{order_id}")
        await callback.answer("تم حذف الطلب")

    finally:
        db.close()
