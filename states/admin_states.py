from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup

class BroadcastState(StatesGroup):
    waiting_for_message = State()