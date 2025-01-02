from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.DatabaseWork.master_fix import MasterDatabase
from app.message_designer.hashzer import hash_callback_suffix_64_name_state


master_db = MasterDatabase()


async def numbers_match(input_match_hash: str = None) -> InlineKeyboardMarkup | None:
    """
    Выводит список всех существующих карт в базе данных master таблице match, и выводит их в виде кнопок.
    По умолчанию создается None хэштег, чтобы можно было просто проверить данную функцию на наличие карт в базе данных.
    Если они все таки есть, то input_match_hash нужно добавить хэштег поиска, для отслеживания нажатия в callback

    :param input_match_hash: укажите хэштег для поиска нажатой кнопки, чтобы callback их отследил (пример: 'SettingMatch')
    :return:
    """
    numbers = await master_db.get_all_match_numbers()

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
