from datetime import datetime
import calendar
import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states.rest import RestStates

from keyboards.rest import (
    get_rest_confirmation_keyboard,
    get_existing_rest_keyboard
)

from database.queries import (
    create_rest,
    get_user_rest,
    extend_rest,
    finish_user_rest,
    finish_expired_rests
)

from services.rest import update_rest_publication


router = Router()


def add_two_months(date: datetime) -> datetime:
    """Возвращает дату через два календарных месяца."""
    month = date.month - 1 + 2
    year = date.year + month // 12
    month = month % 12 + 1

    day = min(
        date.day,
        calendar.monthrange(year, month)[1]
    )

    return date.replace(year=year, month=month, day=day)



@router.callback_query(F.data == "menu:rest")
async def start_rest(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    # Убираем просроченные ресты.
    await finish_expired_rests()

    user = callback.from_user
    existing_rest = await get_user_rest(user.id)

    if existing_rest:
        start_date = datetime.strptime(
            existing_rest["start_date"], "%Y-%m-%d"
        ).strftime("%d.%m.%Y")

        end_date = datetime.strptime(
            existing_rest["end_date"], "%Y-%m-%d"
        ).strftime("%d.%m.%Y")

        await callback.message.edit_caption(
            caption=(
                "<b>У вас уже есть активный рест.</b>\n\n"
                f"Текущий период: {start_date} — {end_date}.\n\n"
                "Что вы хотите сделать?"
            ),
            reply_markup=get_existing_rest_keyboard(),
            parse_mode="HTML"
        )

        await callback.answer()
        return

    await state.set_state(RestStates.waiting_for_dates)

    await callback.message.edit_caption(
        caption=(
            "<b>Оформление реста</b>\n\n"
            "Укажите даты реста в формате ДД.ММ.ГГГГ.\n\n"
            "Например: 10.11.2026 — 25.11.2026.\n\n"
            "Максимальная продолжительность реста — два календарных месяца. "
            "Если вы хотите взять рест на более длительный срок, свяжитесь с владельцем @TovarischOsterman."
        ),
        reply_markup=None,
        parse_mode="HTML"
    )

    await callback.answer()


@router.callback_query(F.data == "rest:change_end")
async def change_rest_end(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user
    existing_rest = await get_user_rest(user.id)

    if not existing_rest:
        await callback.message.edit_caption(
            caption="У вас нет активного реста.",
            reply_markup=None
        )
        await callback.answer()
        return

    await state.update_data(
        rest_start_date=existing_rest["start_date"]
    )

    await state.set_state(RestStates.waiting_for_new_end_date)

    await callback.message.answer(
        "Укажите новую дату окончания реста в формате ДД.ММ.ГГГГ."
    )

    await callback.answer()


@router.message(RestStates.waiting_for_new_end_date)
async def process_new_end_date(message: Message, state: FSMContext):
    try:
        new_end_date = datetime.strptime(
            message.text.strip(), "%d.%m.%Y"
        )
    except (ValueError, AttributeError):
        await message.answer(
            "Неверный формат даты. Используйте ДД.ММ.ГГГГ."
        )
        return

    data = await state.get_data()

    start_date = datetime.strptime(
        data["rest_start_date"], "%Y-%m-%d"
    )

    today = datetime.now().date()

    if new_end_date.date() < today:
        await message.answer("Дата окончания не может быть в прошлом.")
        return

    if new_end_date < start_date:
        await message.answer("Дата окончания не может быть раньше начала реста.")
        return

    if new_end_date > add_two_months(start_date):
        await message.answer(
            "Продолжительность реста не может превышать двух календарных месяцев."
        )
        return

    await extend_rest(
        user_id=message.from_user.id,
        new_end_date=new_end_date.strftime("%Y-%m-%d")
    )

    try:
        await update_rest_publication(message.bot)
    except Exception:
        logging.exception("Не удалось обновить список рестов")

    await message.answer(
        "<b>Дата окончания реста изменена.</b>\n\n"
        f"Новая дата: <b>{new_end_date:%d.%m.%Y}</b>.",
        parse_mode="HTML"
    )

    await state.clear()



@router.callback_query(F.data == "rest:finish")
async def finish_rest(callback: CallbackQuery, state: FSMContext):
    user = callback.from_user

    existing_rest = await get_user_rest(user.id)

    if not existing_rest:
        await callback.message.edit_caption(
            caption="У вас нет активного реста.",
            reply_markup=None
        )
        await callback.answer()
        return

    await finish_user_rest(user.id)

    try:
        await update_rest_publication(callback.bot)
    except Exception:
        logging.exception("Не удалось обновить список рестов")

    await callback.message.edit_caption(
        caption="<b>Ваш рест досрочно завершён.</b>",
        reply_markup=None,
        parse_mode="HTML"
    )

    await state.clear()
    await callback.answer()


@router.message(RestStates.waiting_for_dates)
async def process_rest_dates(message: Message, state: FSMContext):
    try:
        dates = message.text.replace("—", "-").split("-")

        if len(dates) != 2:
            raise ValueError

        start_date = datetime.strptime(dates[0].strip(), "%d.%m.%Y")
        end_date = datetime.strptime(dates[1].strip(), "%d.%m.%Y")

    except (ValueError, AttributeError):
        await message.answer(
            "Неверный формат дат.\n"
            "Используйте формат ДД.ММ.ГГГГ — ДД.ММ.ГГГГ."
        )
        return

    today = datetime.now().date()

    if start_date.date() < today:
        await message.answer("Дата начала реста не может быть в прошлом.")
        return

    if end_date < start_date:
        await message.answer("Дата окончания не может быть раньше даты начала.")
        return

    max_end_date = add_two_months(start_date)

    if end_date > max_end_date:
        await message.answer(
            "Продолжительность реста не может превышать двух календарных месяцев."
        )
        return

    await state.update_data(
        start_date=start_date.strftime("%d.%m.%Y"),
        end_date=end_date.strftime("%d.%m.%Y")
    )

    await state.set_state(RestStates.waiting_for_confirmation)

    await message.answer(
        f"<b>Подтверждение реста</b>\n\n"
        f"Вы хотите взять рест с "
        f"<b>{start_date:%d.%m.%Y}</b> по "
        f"<b>{end_date:%d.%m.%Y}</b>?",
        reply_markup=get_rest_confirmation_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(
    RestStates.waiting_for_confirmation,
    F.data == "rest:edit"
)

async def edit_rest(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RestStates.waiting_for_dates)

    await callback.message.answer(
         "<b>Оформление реста</b>\n\n"
        "Укажите даты реста в формате ДД.ММ.ГГГГ.\n\n"
        "Например: 10.11.2026 — 25.11.2026.\n\n"
        "Максимальная продолжительность реста — два календарных месяца. "
        "Если вы хотите взять рест на более длительный срок, свяжитесь с владельцем @TovarischOsterman.",
        parse_mode="HTML"
    )

    await callback.answer()

@router.callback_query(
    RestStates.waiting_for_confirmation,
    F.data == "rest:confirm"
)

async def confirm_rest(callback: CallbackQuery, state: FSMContext):
    logging.info("CALLBACK: %s", callback.data)
    data = await state.get_data()

    start_date = data["start_date"]
    end_date = data["end_date"]

    user = callback.from_user

    # Проверяем, нет ли уже активного реста.
    existing_rest = await get_user_rest(user.id)

    if existing_rest:
        await callback.message.edit_text(
            "У вас уже есть активный рест.\n\n"
            "Вы можете изменить дату окончания "
            "через раздел «Взять рест»."
        )

        await state.clear()
        await callback.answer()
        return

    # Преобразуем даты в формат SQLite.
    db_start_date = datetime.strptime(
        start_date, "%d.%m.%Y"
    ).strftime("%Y-%m-%d")

    db_end_date = datetime.strptime(
        end_date, "%d.%m.%Y"
    ).strftime("%Y-%m-%d")

    # Сохраняем рест.
    await create_rest(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        start_date=db_start_date,
        end_date=db_end_date
    )

    
    try:
        await update_rest_publication(callback.bot)
    except Exception:
        logging.exception("Не удалось обновить список рестов")

    await callback.message.edit_text(
        "<b>Рест оформлен!</b>\n\n"
        f"Период: {start_date} — {end_date}.",
        parse_mode="HTML"
    )

    await state.clear()
    await callback.answer()
