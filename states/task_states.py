from aiogram.fsm.state import State, StatesGroup

class UserTaskState(StatesGroup):
    waiting_for_comment = State()
    waiting_for_rating = State()