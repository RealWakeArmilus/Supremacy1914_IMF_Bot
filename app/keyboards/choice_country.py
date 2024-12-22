from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.DatabaseWork.match as match_db

from app.message_designer.hashzer import hash_callback_suffix_64_name_state


async def free_countries_match(input_match_hash: str, number_match_db: str) -> InlineKeyboardMarkup | None:
    """
    Выводит список всех свободных государств в базе данных конкретной карты таблице states, и выводит их в виде кнопок.
    По умолчанию создается None хэштег, чтобы можно было просто проверить данную функцию на наличие свободных государств в базе данных.
    Если они все таки есть, то input_match_hash нужно добавить хэштег поиска, для отслеживания нажатия в callback


    :param input_match_hash: укажите хэштег для поиска нажатой кнопки, чтобы callback их отследил (пример: 'ChoiceStateFromMatch_')
    :param number_match_db:
    :return:
    """
    names_country = await match_db.get_free_countries_from_match_for_user(number_match_db)

    if names_country:

        builder = InlineKeyboardBuilder()

        for name_country in names_country:

            callback_data = f"{input_match_hash}_{name_country}"

            hash_callback_data = await hash_callback_suffix_64_name_state(input_match_hash, callback_data, name_country)

            # Ensure callback_data is not None and within limits
            if not hash_callback_data:
                continue  # Skip this button if callback_data is invalid


            button = InlineKeyboardButton(text=str(name_country), callback_data=hash_callback_data)
            builder.add(button)

        builder.adjust(1)

        return builder.as_markup()

    else:
        return None


async def country_verify_by_admin(unique_word: str, number_match: str) -> InlineKeyboardMarkup | None:
    """
    Create keyboards from verify state by admin

    :param number_match:
    :param unique_word:
    :return:
    """
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('✅ Подтвердить'), callback_data=f'ConfirmRequestCountryByAdmin_{unique_word}_{number_match}'))
    builder.add(InlineKeyboardButton(text=str('❌ Отклонить'), callback_data=f'RejectRequestCountryByAdmin_{unique_word}_{number_match}'))

    builder.adjust(1)

    return builder.as_markup()
