from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

router = Router()

ADMIN_ID = 986072050

class SupportState(StatesGroup):
    waiting_for_message = State()

@router.message(F.text == "📞 الدعم الفني")
async def support_start(message: Message, state: FSMContext):
    print("SUPPORT BUTTON PRESSED")
    
    await state.clear()
    await state.set_state(SupportState.waiting_for_message)
    
    await message.answer(
        "📞 الدعم الفني\n"
        "أرسل رسالتك الآن وسيتم إرسالها للإدارة."
    )

@router.message(SupportState.waiting_for_message)
async def send_support_message(message: Message, state: FSMContext):
    try:
        await message.bot.send_message(
            ADMIN_ID,
            f"📩 رسالة دعم جديدة\n"
            f"👤 المستخدم: {message.from_user.full_name}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"{message.text}"
        )

        await message.answer(
            "✅ تم إرسال رسالتك بنجاح.\n"
            "سيتم الرد عليك في أقرب وقت."
        )

    except Exception as e:
        await message.answer(f"❌ حدث خطأ:\n{e}")

    await state.clear()