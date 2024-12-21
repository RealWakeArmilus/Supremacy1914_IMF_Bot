from aiogram import F
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

# Импортируйте модули, которые используются внутри функций
import app.DatabaseWork.master as master_db
import app.keyboards.settings_match as kb

from aiogram import Router

router = Router()


@router.callback_query(F.data == 'settings_match')
async def start_settings_match(callback : CallbackQuery):

    # transition notification create match
    await callback.answer(
        'Вы перешли в настройки карты.',
        reply_markup=ReplyKeyboardRemove())

    if await kb.numbers_match():

        # message from callback to bot admin and delete previous bot message
        await callback.message.edit_text(
            'Выберите номер карты, которую желаете настроить',
            reply_markup=await kb.numbers_match('SettingMatch'),
            parse_mode="html")

    else:

        await callback.message.edit_text(
            'На текущий момент список матчей пуст.',
            parse_mode="html")


@router.callback_query(lambda c: c.data and c.data.startswith('SettingMatch_'))
async def choice_number_match_for_settings(callback: CallbackQuery):

    number_match = callback.data.split('_')[1]

    await callback.answer(f"Вы выбрали матч с номером: {number_match}")

    await callback.message.edit_text(f"Что желаете сделать с матчем: {number_match}",
                                     reply_markup=await kb.edit_match(number_match),
                                     parse_mode="html")


@router.callback_query(lambda c: c.data and c.data.startswith('DeleteMatch_'))
async def deleted_match(callback: CallbackQuery):

    number_match = callback.data.split('_')[1]

    success = await master_db.deleted_match(number_match)

    if success:

        response = f"Номер карты {number_match} был успешно удалён."

    else:

        response = f"Не удалось удалить номер карты {number_match}. Попробуйте позже."

    await callback.answer(response)

    await start_settings_match(callback)
