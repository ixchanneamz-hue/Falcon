from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


class PackageOrderState(StatesGroup):

    waiting_for_post_link = State()

    waiting_for_payment_image = State()