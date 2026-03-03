from aiogram.fsm.state import State, StatesGroup


class AdminMaterialAddStates(StatesGroup):
    name = State()
    category = State()
    type = State()
    price = State()
    unit = State()
    description = State()
    in_stock = State()


class AdminMaterialEditStates(StatesGroup):
    id = State()
    price = State()


class AdminMaterialDeleteStates(StatesGroup):
    id = State()


class AdminCoefficientAddStates(StatesGroup):
    name = State()
    type = State()
    value = State()


class AdminCoefficientEditStates(StatesGroup):
    id = State()
    value = State()


class AdminCoefficientDeleteStates(StatesGroup):
    id = State()
