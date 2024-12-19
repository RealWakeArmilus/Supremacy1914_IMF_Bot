from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db

from app.message_designer.hashzer import hash_callback_suffix_64_name_state


admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать карту', callback_data='created_match')],
    [InlineKeyboardButton(text='Настройки существующих карт', callback_data='settings_match')]
])


types_map = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Великая война')]],
    resize_keyboard=True
)


confirm_created_map = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Подтвердить создание', callback_data='confirm_creation')],
    [InlineKeyboardButton(text='🔄 Начать заново', callback_data='restart_creation')]
])


async def numbers_match(input_match_hash: str = None) -> InlineKeyboardMarkup | None:
    """
    Выводит список всех существующих карт в базе данных master таблице match, и выводит их в виде кнопок.
    По умолчанию создается None хэштег, чтобы можно было просто проверить данную функцию на наличие карт в базе данных.
    Если они все таки есть, то input_match_hash нужно добавить хэштег поиска, для отслеживания нажатия в callback

    :param input_match_hash: укажите хэштег для поиска нажатой кнопки, чтобы callback их отследил (пример: 'SettingMatch')
    :return:
    """
    numbers = await master_db.get_numbers_match()

    if numbers:

        builder = InlineKeyboardBuilder()

        for number in numbers:
            button = InlineKeyboardButton(text=str(number), callback_data=f"{input_match_hash}_{number}")
            builder.add(button)

        builder.adjust(3)

        return builder.as_markup()

    else:
        return None


async def edit_match(number_match: str) -> InlineKeyboardMarkup:
    delete_button = InlineKeyboardButton(text="Удалить", callback_data=f"DeleteMatch_{number_match}")
    return InlineKeyboardMarkup(inline_keyboard=[[delete_button]])


async def free_states_match(input_match_hash: str, number_match_db: str) -> InlineKeyboardMarkup | None:
    """
    Выводит список всех свободных государств в базе данных конкретной карты таблице states, и выводит их в виде кнопок.
    По умолчанию создается None хэштег, чтобы можно было просто проверить данную функцию на наличие свободных государств в базе данных.
    Если они все таки есть, то input_match_hash нужно добавить хэштег поиска, для отслеживания нажатия в callback


    :param input_match_hash: укажите хэштег для поиска нажатой кнопки, чтобы callback их отследил (пример: 'ChoiceStateFromMatch_')
    :param number_match_db:
    :return:
    """
    names_state = await match_db.get_free_states_from_match_for_user(number_match_db)

    if names_state:

        builder = InlineKeyboardBuilder()

        for name_state in names_state:

            callback_data = f"{input_match_hash}_{name_state}"

            hash_callback_data = await hash_callback_suffix_64_name_state(input_match_hash, callback_data, name_state)

            # Ensure callback_data is not None and within limits
            if not hash_callback_data:
                continue  # Skip this button if callback_data is invalid


            button = InlineKeyboardButton(text=str(name_state), callback_data=hash_callback_data)
            builder.add(button)

        builder.adjust(1)

        return builder.as_markup()

    else:
        return None




