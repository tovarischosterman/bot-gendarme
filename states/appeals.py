from aiogram.fsm.state import State, StatesGroup


class AppealStates(StatesGroup):
    waiting_for_message = State()