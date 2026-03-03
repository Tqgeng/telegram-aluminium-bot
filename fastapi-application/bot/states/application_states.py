from aiogram.fsm.state import State, StatesGroup


class ApplicationStates(StatesGroup):
    contact_name = State()
    phone = State()
    email = State()
    address = State()
    description = State()
    photos = State()
    confirm = State()
