from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def nav_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
    )


def step1_construction_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪟 Окна"), KeyboardButton(text="🚪 Двери")],
            [KeyboardButton(text="🏢 Фасады"), KeyboardButton(text="🚧 Перегородки")],
            [KeyboardButton(text="🪟 Витрины"), KeyboardButton(text="✏️ Другое")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step2_profile_model_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="45mm"), KeyboardButton(text="50mm")],
            [KeyboardButton(text="60mm"), KeyboardButton(text="80mm")],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step2_profile_brand_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Rehau"), KeyboardButton(text="Almplast")],
            [KeyboardButton(text="KBE"), KeyboardButton(text="Другой")],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step2_glazing_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Стеклопакет"), KeyboardButton(text="Триплекс")],
            [KeyboardButton(text="Поликарбонат"), KeyboardButton(text="Другое")],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step3_dimensions_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пример: 120 120 2")],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step4_fittings_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Фурнитура: стандарт"),
                KeyboardButton(text="Фурнитура: премиум"),
            ],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step4_mosquito_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Москитная сетка: да"),
                KeyboardButton(text="Москитная сетка: нет"),
            ],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step4_seals_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Уплотнители: стандартные"),
                KeyboardButton(text="Уплотнители: энергосберегающие"),
            ],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step4_sill_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Подоконник: нет")],
            [
                KeyboardButton(text="Подоконник: ПВХ"),
                KeyboardButton(text="Подоконник: камень"),
            ],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step4_install_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Установка: да"),
                KeyboardButton(text="Установка: нет"),
            ],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step5_services_kb(selected: set[str] | None = None) -> ReplyKeyboardMarkup:
    selected = selected or set()

    def mark(name: str) -> str:
        return f"✅ {name}" if name in selected else name

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=mark("Доставка")),
                KeyboardButton(text=mark("Монтаж")),
            ],
            [
                KeyboardButton(text=mark("Демонтаж")),
                KeyboardButton(text=mark("Отделка откосов")),
            ],
            [KeyboardButton(text=mark("Герметизация"))],
            [KeyboardButton(text="✅ Далее"), KeyboardButton(text="◀️ Назад")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def step6_review_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Оформить заявку")],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )
