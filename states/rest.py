from aiogram.fsm.state import State, StatesGroup


class RestStates(StatesGroup):
    waiting_for_dates = State()
    waiting_for_confirmation = State()
    waiting_for_new_end_date = State()