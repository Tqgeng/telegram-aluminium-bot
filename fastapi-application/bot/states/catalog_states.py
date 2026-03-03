from aiogram.fsm.state import State, StatesGroup


class CatalogStates(StatesGroup):
    choose_category = State()
    choose_type = State()
    choose_filters = State()
    list_items = State()
    search_input = State()
