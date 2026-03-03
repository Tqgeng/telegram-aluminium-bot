from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from services.catalog_service import get_catalog

from bot.states.catalog_states import CatalogStates
from bot.keyboards.catalog import catalog_kb, type_kb, filters_kb, list_kb
from bot.keyboards.main_menu import main_menu_kb

router = Router()

PAGE_SIZE = 3

CATEGORY_MAP = {
    "🪟 Окна": "windows",
    "🚪 Двери": "doors",
    "🏢 Фасады": "facades",
    "🚧 Перегородки": "partitions",
    "🪟 Витрины": "showcases",
    "✏️ Другое": "other",
}

TYPE_MAP = {
    "Профиль": "profile",
    "Остекление": "glazing",
    "Фурнитура": "fittings",
    "Комплектующие": "components",
}


@router.message(F.text == "📦 Каталог продуктов")
async def start_catalog(message: Message, state: FSMContext):
    await state.set_state(CatalogStates.choose_category)
    await message.answer("Выберите категорию:", reply_markup=catalog_kb())


@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Заявка отменена", reply_markup=main_menu_kb())


@router.message(F.text == "◀️ Назад")
async def go_back(message: Message, state: FSMContext):
    current = await state.get_state()
    if current == CatalogStates.choose_type:
        await state.set_state(CatalogStates.choose_category)
        await message.answer("Выберите категорию", reply_markup=catalog_kb())
    elif current == CatalogStates.choose_filters:
        await state.set_state(CatalogStates.choose_type)
        await message.answer("Выберите тип", reply_markup=type_kb())
    elif current == CatalogStates.list_items:
        await state.set_state(CatalogStates.choose_filters)
        await message.answer("Настройте фильтры", reply_markup=filters_kb())


@router.message(CatalogStates.choose_category)
async def step_category(message: Message, state: FSMContext):
    await state.update_data(category=CATEGORY_MAP.get(message.text))
    await state.set_state(CatalogStates.choose_type)
    await message.answer("Выберите тип:", reply_markup=type_kb())


@router.message(CatalogStates.choose_type)
async def step_category(message: Message, state: FSMContext):
    await state.update_data(type=TYPE_MAP.get(message.text))
    await state.set_state(CatalogStates.choose_filters)
    await message.answer("Настройте фильтры:", reply_markup=filters_kb())


@router.message(CatalogStates.choose_filters, F.text == "Только в наличии")
async def filter_stock(message: Message, state: FSMContext):
    await state.update_data(in_stock=True)
    await message.answer(
        "Фильтр 'в наличии' применён. Нажмите ✅ Показать.", reply_markup=filters_kb()
    )


@router.message(CatalogStates.choose_filters, F.text.startswith("Цена:"))
async def filter_price(message: Message, state: FSMContext):
    text = message.text
    if "до" in text:
        await state.update_data(price_minimum=None, price_maximum=5000)
    elif "5000-15000" in text:
        await state.update_data(price_minimum=5000, price_maximum=15000)
    else:
        await state.update_data(price_minimum=15000, price_maximum=None)

    await message.answer(
        "Фильтр по цене установлен. Нажмите ✅ Показать.", reply_markup=filters_kb()
    )


@router.message(CatalogStates.choose_filters, F.text == "Поиск по слову")
async def filter_search(message: Message, state: FSMContext):
    await state.set_state(CatalogStates.search_input)
    await message.answer("Введите слово для поиска:")


@router.message(CatalogStates.search_input)
async def filter_search_text(message: Message, state: FSMContext):
    await state.update_data(search=message.text)
    await state.set_state(CatalogStates.choose_filters)
    await message.answer(
        "Поиск установлен. Нажмите ✅ Показать.", reply_markup=filters_kb()
    )


@router.message(CatalogStates.choose_filters, F.text == "✅ Показать")
async def show_list(message: Message, state: FSMContext):
    data = await state.get_data()
    items = await get_catalog(
        category=data.get("category"),
        type_=data.get("type"),
        in_stock=data.get("in_stock"),
        price_minimum=data.get("price_minimum"),
        price_maximum=data.get("price_maximum"),
        search=data.get("search"),
    )
    await state.update_data(items=items, page=0)
    await state.set_state(CatalogStates.list_items)
    await send_page(message, state)


async def send_page(message: Message, state: FSMContext):
    data = await state.get_data()
    items = data.get("items", [])
    page = data.get("page", 0)

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    subset = items[start:end]

    if not subset:
        await message.answer("Ничего не найдено.", reply_markup=main_menu_kb())
        await state.clear()
        return
    lines = []
    for m in subset:
        lines.append(
            f"- {m.name}\n {m.description or 'Без описания'}\n {m.price_per_unit} {m.unit}"
            f"| {'в наличии' if m.in_stock else 'под заказ'}"
        )
    await message.answer("\n\n".join(lines), reply_markup=list_kb())


@router.message(CatalogStates.list_items, F.text == "➡️ Далее")
async def next_page(message: Message, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 0) + 1
    await state.update_data(page=page)
    await send_page(message, state)


@router.message(CatalogStates.list_items, F.text == "⬅️ Назад")
async def prev_page(message: Message, state: FSMContext):
    data = await state.get_data()
    page = max(0, data.get("page", 0) - 1)
    await state.update_data(page=page)
    await send_page(message, state)


@router.message(CatalogStates.list_items, F.text == "🏠 Главное меню")
async def back_to_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню", reply_markup=main_menu_kb())
