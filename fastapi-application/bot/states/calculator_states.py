from aiogram.fsm.state import StatesGroup, State


class CalculatorStates(StatesGroup):
    # Шаг 1
    choose_construction = State()

    # Шаг 2 (подшаги)
    choose_profile_model = State()
    choose_profile_brand = State()
    choose_glazing_type = State()

    # Шаг 3
    input_dimensions = State()

    # Шаг 4 (подшаги)
    choose_fittings = State()
    choose_mosquito = State()
    choose_seals = State()
    choose_sill = State()
    choose_installation = State()

    # Шаг 5
    choose_services = State()

    # Шаг 6
    review = State()
