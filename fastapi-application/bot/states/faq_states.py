from aiogram.fsm.state import State, StatesGroup


class FAQStates(StatesGroup):
    waiting_query = State()
