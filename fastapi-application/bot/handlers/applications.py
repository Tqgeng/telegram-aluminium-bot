from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.services.notification_service import (
    notify_manager,
    notify_user,
    mark_manager_viewed,
)
from bot.states.application_states import ApplicationStates
from bot.keyboards.calculator import step6_review_kb
from bot.keyboards.main_menu import main_menu_kb
from bot.keyboards.application import nav_kb, photos_kb, confirm_kb, apps_list_kb
from bot.utils.validators import is_valid_phone, normalize_phone
from bot.services.user_service import (
    update_user_phone,
    get_user_by_telegram_id,
    get_or_create_user,
    get_user_by_id,
)
from services.application_service import (
    create_application,
    list_user_applications,
    set_application_status,
    get_application,
)

router = Router()

STATUS_LABELS = {
    "new": "Новая",
    "in_progress": "В работе",
    "completed": "Завершена",
    "rejected": "Отклонена",
}

MAX_FILES = 5
PAGE_SIZE = 5


async def _append_file(
    state: FSMContext,
    file_id: str,
    file_path: str | None,
    ftype: str,
):
    data = await state.get_data()
    files = data.get("photos", [])
    if len(files) >= MAX_FILES:
        return None, files
    files.append({"file_id": file_id, "file_path": file_path, "type": ftype})
    await state.update_data(photos=files)
    return len(files), files


@router.callback_query(F.data.startswith("app_accept:"))
async def manager_accept(call: CallbackQuery):
    app_id = int(call.data.split(":")[1])
    user_id = await set_application_status(app_id, "in_progress")
    if user_id:
        user = await get_user_by_id(user_id)
        if user and user.telegram_id:
            await notify_user(call.message.bot, user.telegram_id, app_id, "in_progress")
    await mark_manager_viewed(app_id)
    await call.answer("Заявка взята в работу")


@router.callback_query(F.data.startswith("app_call:"))
async def manager_call(call: CallbackQuery):
    app_id = int(call.data.split(":")[1])
    app = await get_application(app_id)
    await call.message.answer(f"Телефон клиента: {app.phone}")
    await call.answer()


@router.callback_query(F.data.startswith("app_sms:"))
async def manager_sms(call: CallbackQuery):
    app_id = int(call.data.split(":")[1])
    app = await get_application(app_id)
    await call.message.answer(f"SMS клиенту: {app.phone}")
    await call.answer()


@router.message(F.text == "✅ Оформить заявку")
async def start_application(message: Message, state: FSMContext):
    user = await get_or_create_user(
        telegram_id=message.from_user.id,
        name=message.from_user.full_name,
    )
    await state.update_data(user_id=user.id)
    await state.set_state(ApplicationStates.contact_name)
    await message.answer("Введите контактное имя:", reply_markup=nav_kb())


@router.message(F.text == "📝 Мои заявки")
async def my_apps(message: Message):
    user = await get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("У вас пока нет заявок.")
        return

    apps = await list_user_applications(user.id)
    if not apps:
        await message.answer("У вас пока нет заявок.")
        return

    page = apps[:PAGE_SIZE]
    next_offset = PAGE_SIZE if len(apps) > PAGE_SIZE else None

    lines = ["Ваши заявки:"]
    for app in page:
        status_key = (
            app.status.value if hasattr(app.status, "value") else str(app.status)
        )
        status = STATUS_LABELS.get(status_key, status_key)
        cost = app.estimated_cost
        lines.append(f"#{app.id} - {status} - {app.created_at:%d.%m.%Y} - {cost} руб")
    await message.answer(
        "\n".join(lines),
        reply_markup=apps_list_kb([a.id for a in page], next_offset=next_offset),
    )


@router.callback_query(F.data.startswith("app_detail:"))
async def app_detail(call: CallbackQuery):
    app_id = int(call.data.split(":")[1])
    app = await get_application(app_id)
    status_key = app.status.value if hasattr(app.status, "value") else str(app.status)
    status = STATUS_LABELS.get(status_key, status_key)
    if not app:
        await call.answer("Заявка не найдена", show_alert=True)
        return
    text = (
        f"📋 Заявка #{app.id}\n"
        f"Статус: {status}\n"
        f"Имя: {app.contact_name}\n"
        f"Телефон: {app.phone}\n"
        f"Email: {app.email or '-'}\n"
        f"Адрес: {app.address}\n"
        f"Описание: {app.description or '-'}\n"
        f"Стоимость: {app.estimated_cost or '-'} руб\n"
        f"Дата: {app.created_at:%d.%m.%Y}"
    )
    await call.message.answer(text)
    await call.answer()


@router.callback_query(F.data.startswith("app_more:"))
async def app_more(call: CallbackQuery):
    offset = int(call.data.split(":")[1])
    user = await get_user_by_telegram_id(call.from_user.id)
    if not user:
        await call.answer()
        return
    apps = await list_user_applications(user.id)
    page = apps[offset : offset + PAGE_SIZE]
    next_offset = offset + PAGE_SIZE if len(apps) > offset + PAGE_SIZE else None
    if not page:
        await call.answer("Больше заявок нет", show_alert=True)
        return
    lines = ["Ваши заявки (продолжение):"]
    for app in page:
        status_key = (
            app.status.value if hasattr(app.status, "value") else str(app.status)
        )
        status = STATUS_LABELS.get(status_key, status_key)
        cost = app.estimated_cost
        lines.append(f"#{app.id} - {status} - {app.created_at:%d.%m.%Y} - {cost} руб")
    await call.message.answer(
        "\n".join(lines),
        reply_markup=apps_list_kb([a.id for a in page], next_offset=next_offset),
    )
    await call.answer()


@router.message(F.text == "❌ Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Заявка отменена", reply_markup=step6_review_kb())


@router.message(F.text == "◀️ Назад")
async def go_back(message: Message, state: FSMContext):
    current = await state.get_state()
    if current == ApplicationStates.phone:
        await state.set_state(ApplicationStates.contact_name)
        await message.answer("Введите контактное имя:", reply_markup=nav_kb())
    elif current == ApplicationStates.email:
        await state.set_state(ApplicationStates.phone)
        await message.answer("Введите номер телефона:", reply_markup=nav_kb())
    elif current == ApplicationStates.address:
        await state.set_state(ApplicationStates.email)
        await message.answer(
            "Введите email (или пропустите '-'):", reply_markup=nav_kb()
        )
    elif current == ApplicationStates.description:
        await state.set_state(ApplicationStates.address)
        await message.answer("Введите адрес объекта:", reply_markup=nav_kb())
    elif current == ApplicationStates.photos:
        await state.set_state(ApplicationStates.description)
        await message.answer(
            "Кратко опишите проект (до 500 символов):", reply_markup=nav_kb()
        )
    elif current == ApplicationStates.confirm:
        await state.set_state(ApplicationStates.photos)
        await message.answer(
            "Пришлите фото (до 5) или нажмите ✅ Готово:", reply_markup=photos_kb()
        )
    else:
        await message.answer("Вы уже на первом шаге.", reply_markup=nav_kb())


@router.message(ApplicationStates.contact_name)
async def step_name(message: Message, state: FSMContext):
    await state.update_data(contact_name=message.text)
    await state.set_state(ApplicationStates.phone)
    await message.answer("Введите номер телефона:", reply_markup=nav_kb())


@router.message(ApplicationStates.phone)
async def step_phone(message: Message, state: FSMContext):
    if not is_valid_phone(message.text):
        await message.answer(
            "Неверный формат. Пример: +79991234567", reply_markup=nav_kb()
        )
        return
    phone = normalize_phone(message.text)
    await state.update_data(phone=phone)
    await update_user_phone(message.from_user.id, phone)
    await state.set_state(ApplicationStates.email)
    await message.answer("Введите email (или пропустите '-'):", reply_markup=nav_kb())


@router.message(ApplicationStates.email)
async def step_email(message: Message, state: FSMContext):
    email = message.text if message.text != "-" else None
    await state.update_data(email=email)
    await state.set_state(ApplicationStates.address)
    await message.answer("Введите адрес объекта:", reply_markup=nav_kb())


@router.message(ApplicationStates.address)
async def step_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(ApplicationStates.description)
    await message.answer(
        "Кратко опишите проект (до 500 символов):", reply_markup=nav_kb()
    )


@router.message(ApplicationStates.description)
async def step_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(ApplicationStates.photos)
    await message.answer(
        "Пришлите фото (до 5) или нажмите ✅ Готово:", reply_markup=photos_kb()
    )


@router.message(ApplicationStates.photos, F.photo)
async def step_photo(message: Message, state: FSMContext):
    file = await message.bot.get_file(message.photo[-1].file_id)
    count, files = await _append_file(
        state, message.photo[-1].file_id, file.file_path, "photo"
    )
    if count is None:
        await message.answer("Можно максимум 5 фото.", reply_markup=photos_kb())
        return
    await message.answer(
        f"Фото добавлено ({count}/{MAX_FILES}). Можно еще или нажмите ✅ Готово",
        reply_markup=photos_kb(),
    )


@router.message(ApplicationStates.photos, F.document)
async def step_doc(message: Message, state: FSMContext):
    file = await message.bot.get_file(message.document.file_id)
    count, files = await _append_file(
        state, message.document.file_id, file.file_path, "document"
    )
    if count is None:
        await message.answer("Можно максимум 5 файлов.", reply_markup=photos_kb())
        return
    await message.answer(
        f"Файл добавлен ({count}/{MAX_FILES}). Можно еще или нажмите ✅ Готово",
        reply_markup=photos_kb(),
    )


@router.message(ApplicationStates.photos, F.text == "✅ Готово")
async def step_photos_done(message: Message, state: FSMContext):
    await state.set_state(ApplicationStates.confirm)
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
        f"ИТОГО: {calc.get('total_cost')} руб\n\n"
        "📋 Данные заявки:\n"
        f"Имя: {data.get('contact_name')}\n"
        f"Телефон: {data.get('phone')}\n"
        f"Email: {data.get('email') or '-'}\n"
        f"Адрес: {data.get('address')}\n"
        f"Описание: {data.get('description')}"
    )

    await message.answer(text, reply_markup=confirm_kb())


@router.message(ApplicationStates.confirm, F.text == "✅ Отправить заявку")
async def submit_application(message: Message, state: FSMContext):
    data = await state.get_data()
    app_id = await create_application(
        {
            "user_id": data.get("user_id"),
            "contact_name": data.get("contact_name"),
            "phone": data.get("phone"),
            "email": data.get("email"),
            "address": data.get("address"),
            "description": data.get("description"),
            "photos": data.get("photos", []),
            "estimated_cost": data.get("estimated_cost"),
        }
    )
    text = (
        "🆕 НОВАЯ ЗАЯВКА\n\n"
        f"👤 {data.get('contact_name')}\n"
        f"📱 {data.get('phone')}\n"
        f"📍 {data.get('address')}\n"
        f"📋 {data.get('construction_type')} {data.get('width_cm')}×{data.get('height_cm')} см"
        f" Предварительная стоимость: {data.get('estimated_cost')}"
    )
    await notify_manager(message.bot, app_id, text, data.get("phone"))
    await state.clear()
    await message.answer(
        f"Заявка отправлена! ID: {app_id}\nМенеджер свяжется с вами.",
        reply_markup=main_menu_kb(),
    )
