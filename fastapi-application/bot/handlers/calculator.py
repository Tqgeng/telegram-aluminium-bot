from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from decimal import Decimal
import re

from bot.states.calculator_states import CalculatorStates
from bot.keyboards.main_menu import main_menu_kb
from services.calculator_service import calculate, CalcInput, save_calculation
from bot.services.user_service import get_user_by_telegram_id
from bot.keyboards.calculator import (
    step1_construction_kb,
    step2_profile_model_kb,
    step2_profile_brand_kb,
    step2_glazing_kb,
    step3_dimensions_kb,
    step4_fittings_kb,
    step4_mosquito_kb,
    step4_seals_kb,
    step4_sill_kb,
    step4_install_kb,
    step5_services_kb,
    step6_review_kb,
)

router = Router()

SERVICE_OPTIONS = {
    "Доставка",
    "Монтаж",
    "Демонтаж",
    "Отделка откосов",
    "Герметизация",
}


def normalize_service(text: str) -> str:
    return text.replace("✅ ", "")


@router.message(F.text == "📋 Рассчитать стоимость")
async def start_calc(message: Message, state: FSMContext):
    await state.set_state(CalculatorStates.choose_construction)
    await message.answer(
        "Шаг 1/6: Выберите тип конструкции", reply_markup=step1_construction_kb()
    )


@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Расчет отменен.", reply_markup=main_menu_kb())


@router.message(F.text == "◀️ Назад")
async def go_back(message: Message, state: FSMContext):
    current = await state.get_state()

    if current == CalculatorStates.choose_profile_model:
        await state.set_state(CalculatorStates.choose_construction)
        await message.answer(
            "Шаг 1/6: Выберите тип конструкции", reply_markup=step1_construction_kb()
        )

    elif current == CalculatorStates.choose_profile_brand:
        await state.set_state(CalculatorStates.choose_profile_model)
        await message.answer(
            "Шаг 2.1/6: Модель профиля", reply_markup=step2_profile_model_kb()
        )

    elif current == CalculatorStates.choose_glazing_type:
        await state.set_state(CalculatorStates.choose_profile_brand)
        await message.answer(
            "Шаг 2.2/6: Бренд профиля", reply_markup=step2_profile_brand_kb()
        )

    elif current == CalculatorStates.input_dimensions:
        await state.set_state(CalculatorStates.choose_glazing_type)
        await message.answer(
            "Шаг 2.3/6: Тип остекления", reply_markup=step2_glazing_kb()
        )

    elif current == CalculatorStates.choose_fittings:
        await state.set_state(CalculatorStates.input_dimensions)
        await message.answer(
            "Шаг 3/6: Введите размеры", reply_markup=step3_dimensions_kb()
        )

    elif current == CalculatorStates.choose_mosquito:
        await state.set_state(CalculatorStates.choose_fittings)
        await message.answer("Шаг 4.1/6: Фурнитура", reply_markup=step4_fittings_kb())

    elif current == CalculatorStates.choose_seals:
        await state.set_state(CalculatorStates.choose_mosquito)
        await message.answer(
            "Шаг 4.2/6: Москитная сетка", reply_markup=step4_mosquito_kb()
        )

    elif current == CalculatorStates.choose_sill:
        await state.set_state(CalculatorStates.choose_seals)
        await message.answer("Шаг 4.3/6: Уплотнители", reply_markup=step4_seals_kb())

    elif current == CalculatorStates.choose_installation:
        await state.set_state(CalculatorStates.choose_sill)
        await message.answer("Шаг 4.4/6: Подоконник", reply_markup=step4_sill_kb())

    elif current == CalculatorStates.choose_services:
        await state.set_state(CalculatorStates.choose_installation)
        await message.answer("Шаг 4.5/6: Установка", reply_markup=step4_install_kb())

    elif current == CalculatorStates.review:
        await state.set_state(CalculatorStates.choose_services)
        data = await state.get_data()
        selected = set(data.get("services", []))
        await message.answer(
            "Шаг 5/6: Доп. услуги", reply_markup=step5_services_kb(selected)
        )

    else:
        await message.answer(
            "Вы уже на первом шаге.", reply_markup=step1_construction_kb()
        )


# Шаг 1
@router.message(CalculatorStates.choose_construction)
async def step1(message: Message, state: FSMContext):
    await state.update_data(construction_type=message.text)
    await state.set_state(CalculatorStates.choose_profile_model)
    await message.answer(
        "Шаг 2.1/6: Модель профиля", reply_markup=step2_profile_model_kb()
    )


# Шаг 2.1
@router.message(CalculatorStates.choose_profile_model)
async def step2_1(message: Message, state: FSMContext):
    await state.update_data(profile_model=message.text)
    await state.set_state(CalculatorStates.choose_profile_brand)
    await message.answer(
        "Шаг 2.2/6: Бренд профиля", reply_markup=step2_profile_brand_kb()
    )


# Шаг 2.2
@router.message(CalculatorStates.choose_profile_brand)
async def step2_2(message: Message, state: FSMContext):
    await state.update_data(profile_brand=message.text)
    await state.set_state(CalculatorStates.choose_glazing_type)
    await message.answer("Шаг 2.3/6: Тип остекления", reply_markup=step2_glazing_kb())


# Шаг 2.3
@router.message(CalculatorStates.choose_glazing_type)
async def step2_3(message: Message, state: FSMContext):
    await state.update_data(glazing_type=message.text)
    await state.set_state(CalculatorStates.input_dimensions)
    await message.answer(
        "Шаг 3/6: Введите размеры (ШхВ, см) и количество",
        reply_markup=step3_dimensions_kb(),
    )


# Шаг 3
@router.message(CalculatorStates.input_dimensions)
async def step3(message: Message, state: FSMContext):
    raw = message.text.strip()
    m = re.match(r"^(\d+(?:[.,]\d+)?)\s+(\d+(?:[.,]\d+)?)\s+(\d+)$", raw)
    if not m:
        await message.answer(
            "Формат: ширина высота количество. Пример: 120 120 2",
            reply_markup=step3_dimensions_kb(),
        )
        return

    w = Decimal(m.group(1).replace(",", "."))
    h = Decimal(m.group(2).replace(",", "."))
    q = int(m.group(3))

    await state.update_data(width_cm=str(w), height_cm=str(h), quantity=q)
    await state.set_state(CalculatorStates.choose_fittings)
    await message.answer("Шаг 4.1/6: Фурнитура", reply_markup=step4_fittings_kb())


# Шаг 4.1
@router.message(CalculatorStates.choose_fittings)
async def step4_1(message: Message, state: FSMContext):
    await state.update_data(fittings=message.text)
    await state.set_state(CalculatorStates.choose_mosquito)
    await message.answer("Шаг 4.2/6: Москитная сетка", reply_markup=step4_mosquito_kb())


# Шаг 4.2
@router.message(CalculatorStates.choose_mosquito)
async def step4_2(message: Message, state: FSMContext):
    await state.update_data(mosquito=message.text)
    await state.set_state(CalculatorStates.choose_seals)
    await message.answer("Шаг 4.3/6: Уплотнители", reply_markup=step4_seals_kb())


# Шаг 4.3
@router.message(CalculatorStates.choose_seals)
async def step4_3(message: Message, state: FSMContext):
    await state.update_data(seals=message.text)
    await state.set_state(CalculatorStates.choose_sill)
    await message.answer("Шаг 4.4/6: Подоконник", reply_markup=step4_sill_kb())


# Шаг 4.4
@router.message(CalculatorStates.choose_sill)
async def step4_4(message: Message, state: FSMContext):
    await state.update_data(sill=message.text)
    await state.set_state(CalculatorStates.choose_installation)
    await message.answer("Шаг 4.5/6: Установка", reply_markup=step4_install_kb())


# Шаг 4.5
@router.message(CalculatorStates.choose_installation)
async def step4_5(message: Message, state: FSMContext):
    await state.update_data(installation=message.text)
    await state.set_state(CalculatorStates.choose_services)
    await message.answer("Шаг 5/6: Доп. услуги", reply_markup=step5_services_kb())


# Шаг 5
@router.message(CalculatorStates.choose_services, F.text == "✅ Далее")
async def step5_next(message: Message, state: FSMContext):
    data = await state.get_data()

    inp = CalcInput(
        width_cm=Decimal(data["width_cm"]),
        height_cm=Decimal(data["height_cm"]),
        quantity=int(data["quantity"]),
        profile_name=data["profile_model"],
        glazing_name=data["glazing_type"],
        fittings_name=data["fittings"],
        package_names=[data["mosquito"], data["seals"], data["sill"]],
        service_names=data.get("services", []),
        complexity_name="Базовая сложность",
    )

    result = await calculate(inp)

    await state.update_data(estimated_cost=str(result.total_cost))

    user = await get_user_by_telegram_id(message.from_user.id)
    calc_id = await save_calculation(
        inp,
        result,
        user_id=user.id if user else None,
        construction_type=data.get("construction_type"),
        profile_system=f"{data.get('profile_system')} / {data.get('profile_brand')}",
    )
    await state.update_data(calc_id=calc_id)

    await state.update_data(
        calc_result={
            "material_cost": str(result.material_cost),
            "labor_cost": str(result.labor_cost),
            "delivery_cost": str(result.delivery_cost),
            "discount_value": str(result.discount_value),
            "total_cost": str(result.total_cost),
        }
    )

    await state.set_state(CalculatorStates.review)
    data = await state.get_data()
    calc = data.get("calc_result", {})

    services = data.get("services", [])
    services_text = ", ".join(services) if services else "нет"

    text = (
        "🧾 Проверка данных\n\n"
        f"Тип: {data.get('construction_type')}\n"
        f"Профиль: {data.get('profile_model')} / {data.get('profile_brand')}\n"
        f"Остекление: {data.get('glazing_type')}\n"
        f"Размеры: {data.get('width_cm')}×{data.get('height_cm')} см, "
        f"кол-во: {data.get('quantity')}\n"
        f"Фурнитура: {data.get('fittings')}\n"
        f"Сетка: {data.get('mosquito')}\n"
        f"Уплотнители: {data.get('seals')}\n"
        f"Подоконник: {data.get('sill')}\n"
        f"Установка: {data.get('installation')}\n"
        f"Доп. услуги: {services_text}\n\n"
        "💰 Итоговый расчет:\n"
        f"Материалы: {calc.get('material_cost')} руб\n"
        f"Работы: {calc.get('labor_cost')} руб\n"
        f"Доставка: {calc.get('delivery_cost')} руб\n"
        f"Скидка: -{calc.get('discount_value')} руб\n"
        f"ИТОГО: {calc.get('total_cost')} руб"
    )

    await message.answer(text, reply_markup=step6_review_kb())


@router.message(CalculatorStates.choose_services)
async def step5_toggle(message: Message, state: FSMContext):
    service = normalize_service(message.text)
    if service not in SERVICE_OPTIONS:
        return
    data = await state.get_data()
    selected = set(data.get("services", []))
    if service in selected:
        selected.remove(service)
    else:
        selected.add(service)
    await state.update_data(services=list(selected))
    await message.answer(
        "Выберите доп. услуги (можно несколько):",
        reply_markup=step5_services_kb(selected),
    )
