from aiogram.fsm.state import State, StatesGroup


class WithdrawState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_account = State()