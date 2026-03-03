import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.utils.admin import is_group_admin
from services.catalog_service import get_catalog
from services.stats_service import get_stats
from bot.states.admin_states import (
    AdminMaterialAddStates,
    AdminMaterialEditStates,
    AdminMaterialDeleteStates,
    AdminCoefficientAddStates,
    AdminCoefficientEditStates,
    AdminCoefficientDeleteStates,
)
from services.materials_service import (
    add_material,
    update_material,
    delete_material,
)
from services.coefficients_service import (
    add_coefficient,
    update_coefficient,
    delete_coefficient,
    list_coefficient,
)

logger = logging.getLogger("admin")
router = Router()


@router.message(F.text == "/stats")
async def stats(message: Message):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    total, avg_check = await get_stats()
    logger.info(
        "admin=%s action=stats payload=%s",
        message.from_user.id,
        message.text,
    )
    await message.answer(
        f"📊Статистика\n Всего заявок: {total}\n Средний чек: {avg_check:.2f} руб."
    )


# material


@router.message(F.text == "/materials")
async def list_materials(message: Message):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    items = await get_catalog()
    if not items:
        await message.answer("Материалы не найдены")
        return
    lines = [f"{m.id}. {m.name} - {m.price_per_unit} {m.unit}" for m in items[:50]]
    logger.info(
        "admin=%s action=materials_list payload=%s",
        message.from_user.id,
        message.text,
    )
    await message.answer("Материалы:\n" + "\n".join(lines))


@router.message(F.text == "/material_add")
async def material_add(message: Message, state: FSMContext):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminMaterialAddStates.name)
    await message.answer("Введите название материала:")


@router.message(AdminMaterialAddStates.name)
async def material_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminMaterialAddStates.category)
    await message.answer(
        "Категория (windows/doors/facades/partitions/showcases/others):"
    )


@router.message(AdminMaterialAddStates.category)
async def material_category(message: Message, state: FSMContext):
    await state.update_data(category=message.text)
    await state.set_state(AdminMaterialAddStates.type)
    await message.answer("Тип (profile/glazing/fittings/components):")


@router.message(AdminMaterialAddStates.type)
async def material_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await state.set_state(AdminMaterialAddStates.price)
    await message.answer("Цена:")


@router.message(AdminMaterialAddStates.price)
async def material_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AdminMaterialAddStates.unit)
    await message.answer("Ед. измерения (м2/м.п./шт):")


@router.message(AdminMaterialAddStates.unit)
async def material_unit(message: Message, state: FSMContext):
    await state.update_data(unit=message.text)
    await state.set_state(AdminMaterialAddStates.description)
    await message.answer("В наличии? (1/0):")


@router.message(AdminMaterialAddStates.description)
async def material_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AdminMaterialAddStates.in_stock)
    await message.answer("Описание:")


@router.message(AdminMaterialAddStates.in_stock)
async def material_in_stock(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await add_material(
            data["name"],
            data["category"],
            data["type"],
            data["price"],
            data["unit"],
            data["description"],
            message.text == "1",
        )
        logger.info(
            "admin=%s action=material_add payload=%s",
            message.from_user.id,
            message.text,
        )
        await message.answer("✅ Материал добавлен")
    except Exception as e:
        logger.warning(
            "admin=%s action=material_add_failed err=%s payload=%s",
            message.from_user.id,
            e,
            message.text,
        )
        await message.answer(f"Ошибка: {e}")
    await state.clear()


@router.message(F.text == "/material_edit")
async def material_edit(message: Message, state: FSMContext):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminMaterialEditStates.id)
    await message.answer("Введите ID материала:")


@router.message(AdminMaterialEditStates.id)
async def material_edit_id(message: Message, state: FSMContext):
    await state.update_data(id=message.id)
    await state.set_state(AdminMaterialEditStates.price)
    await message.answer("Введите новую цену:")


@router.message(AdminMaterialEditStates.price)
async def material_edit_price(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await update_material(int(data["id"]), message.text)
        logger.info(
            "admin=%s action=material_edit payload=%s",
            message.from_user.id,
            message.text,
        )
        await message.answer("✅ Материал обновлён.")
    except Exception as e:
        logger.warning(
            "admin=%s action=material_edit_failed err=%s payload=%s",
            message.from_user.id,
            e,
            message.text,
        )
        await message.answer(f"Ошибка: {e}")
    await state.clear()


@router.message(F.text == "/material_delete")
async def material_delete(message: Message, state: FSMContext):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminMaterialDeleteStates.id)
    await message.answer("Введите ID материала:")


@router.message(AdminMaterialDeleteStates.id)
async def material_delete_id(message: Message, state: FSMContext):
    try:
        await delete_material(int(message.text))
        logger.info(
            "admin=%s action=material_delete payload=%s",
            message.from_user.id,
            message.text,
        )
        await message.answer("✅ Материал удален.")
    except Exception as e:
        logger.warning(
            "admin=%s action=material_delete_failed err=%s payload=%s",
            message.from_user.id,
            e,
            message.text,
        )
        await message.answer(f"Ошибка: {e}")
    await state.clear()


# - coefficient


@router.message(F.text == "/coeffs")
async def list_materials(message: Message):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    items = await list_coefficient()
    if not items:
        await message.answer("Коэффициентов нет")
        return
    lines = [f"{c.id}. {c.name} | {c.value}" for c in items[:50]]
    logger.info(
        "admin=%s action=coeffs_list payload=%s",
        message.from_user.id,
        message.text,
    )
    await message.answer("Коэффициенты:\n" + "\n".join(lines))


@router.message(F.text == "/coeff_add")
async def coeff_add_start(message: Message, state: FSMContext):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminCoefficientAddStates.name)
    await message.answer("Введите название коэффициента:")


@router.message(AdminCoefficientAddStates.name)
async def coeff_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AdminCoefficientAddStates.type)
    await message.answer("Тип (complexity/region/discount/seasonal/promo):")


@router.message(AdminCoefficientAddStates.type)
async def coeff_type(message: Message, state: FSMContext):
    await state.update_data(type=message.text)
    await state.set_state(AdminCoefficientAddStates.value)
    await message.answer("Значение (например 1.2 или 0.05):")


@router.message(AdminCoefficientAddStates.value)
async def coeff_value(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await add_coefficient(data["name"], data["type"], message.text)
        logger.info(
            "admin=%s action=coeff_add payload=%s",
            message.from_user.id,
            message.text,
        )
        await message.answer("✅ Коэффициент добавлен.")
    except Exception as e:
        logger.warning(
            "admin=%s action=coeff_add_failed err=%s payload=%s",
            message.from_user.id,
            e,
            message.text,
        )
        await message.answer(f"Ошибка: {e}")
    await state.clear()


@router.message(F.text == "/coeff_edit")
async def coeff_edit_start(message: Message, state: FSMContext):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminCoefficientEditStates.id)
    await message.answer("Введите ID коэффициента:")


@router.message(AdminCoefficientEditStates.id)
async def coeff_edit_id(message: Message, state: FSMContext):
    await state.update_data(id=message.text)
    await state.set_state(AdminCoefficientEditStates.value)
    await message.answer("Введите новое значение:")


@router.message(AdminCoefficientEditStates.value)
async def coeff_edit_value(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await update_coefficient(int(data["id"]), message.text)
        logger.info(
            "admin=%s action=coeff_edit payload=%s",
            message.from_user.id,
            message.text,
        )
        await message.answer("✅ Коэффициент обновлён.")
    except Exception as e:
        logger.warning(
            "admin=%s action=coeff_edit_failed err=%s payload=%s",
            message.from_user.id,
            e,
            message.text,
        )
        await message.answer(f"Ошибка: {e}")
    await state.clear()


@router.message(F.text == "/coeff_delete")
async def coeff_delete_start(message: Message, state: FSMContext):
    if not await is_group_admin(message):
        await message.answer("❌ Нет прав.")
        return
    await state.set_state(AdminCoefficientDeleteStates.id)
    await message.answer("Введите ID коэффициента:")


@router.message(AdminCoefficientDeleteStates.id)
async def coeff_delete_id(message: Message, state: FSMContext):
    try:
        await delete_coefficient(int(message.text))
        logger.info(
            "admin=%s action=coeff_delete payload=%s",
            message.from_user.id,
            message.text,
        )
        await message.answer("✅ Коэффициент удалён.")
    except Exception as e:
        logger.warning(
            "admin=%s action=coeff_delete_failed err=%s payload=%s",
            message.from_user.id,
            e,
            message.text,
        )
        await message.answer(f"Ошибка: {e}")
    await state.clear()
