from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def catalog_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🪟 Окна"), KeyboardButton(text="🚪 Двери")],
            [KeyboardButton(text="🏢 Фасады"), KeyboardButton(text="🚧 Перегородки")],
            [KeyboardButton(text="🪟 Витрины"), KeyboardButton(text="️✏️ Другое")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def type_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Профиль"), KeyboardButton(text="Остекление")],
            [KeyboardButton(text="Фурнитура"), KeyboardButton(text="Комплектующие")],
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def filters_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Только в наличии")],
            [
                KeyboardButton(text="Цена: до 5000"),
                KeyboardButton(text="Цена: 5000-15000"),
            ],
            [KeyboardButton(text="Цена: от 15000")],
            [KeyboardButton(text="Поиск по слову")],
            [KeyboardButton(text="✅ Показать"), KeyboardButton(text="◀️ Назад")],
            [KeyboardButton(text="❌ Отмена")],
        ],
        resize_keyboard=True,
    )


def list_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="◀️ Назад"), KeyboardButton(text="✅ Далее")],
            [KeyboardButton(text="🏠 Главное меню")],
        ],
        resize_keyboard=True,
    )
