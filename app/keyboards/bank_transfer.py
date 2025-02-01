from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.DatabaseWork.database import DatabaseManager


async def busy_countries_match(ignor_country_name: str, input_match_hash: str, number_match_db: str) -> InlineKeyboardMarkup | None:
    """
    Выводит список всех занятых государств в базе данных конкретной карты таблице states, и выводит их в виде кнопок.
    По умолчанию создается None хэштег, чтобы можно было просто проверить данную функцию на наличие свободных государств в базе данных.
    Если они все таки есть, то input_match_hash нужно добавить хэштег поиска, для отслеживания нажатия в callback

    :param ignor_country_name: Название государства который нужно проигнорировать. В данном случае, то государства кто создает перевод. Самому себе перевод он не сможет создать.
    :param input_match_hash: Укажите хэштег для поиска нажатой кнопки, чтобы callback их отследил (пример: 'BeneficiaryBankTransfer_')
    :param number_match_db: номер матча
    :return:
    """
    names_country = await DatabaseManager(database_path=number_match_db).get_countries_names(busy=True)

    if names_country:

        builder = InlineKeyboardBuilder()

        for name_country in names_country:

            if name_country != ignor_country_name:

                country_id = await DatabaseManager(database_path=number_match_db).get_country_id(
                    country_name=name_country)

                callback_data = f"{input_match_hash}_{number_match_db}_{country_id}"

                button = InlineKeyboardButton(text=str(name_country), callback_data=callback_data)
                builder.add(button)

        builder.adjust(1)

        builder.as_markup()

        if str(builder.as_markup()) != 'inline_keyboard=[]':
            return builder.as_markup()
        else:
            return None


async def get_currencies_capitals_from_country(data_currency_capitals_from_country: list, input_match_hash: str, number_match_db: str) -> InlineKeyboardMarkup | None:
    """
    :param data_currency_capitals_from_country: [{'currency_id': 4, 'country_27': 50000000.0, 'currency_name': 'доллар', 'currency_tick': 'USD'}]
    :param input_match_hash: Укажите хэштег для поиска нажатой кнопки, чтобы callback их отследил (пример: 'BeneficiaryBankTransfer_')
    :param number_match_db: номер матча
    :return: Выводит список всех доступных валют, которыми владеет государство на данный момент в нужном количестве для сделки.
    """
    if data_currency_capitals_from_country:

        builder = InlineKeyboardBuilder()

        for data_currency_capital in data_currency_capitals_from_country:

            text = f'{data_currency_capital['currency_name']} ({data_currency_capital['currency_tick']})'

            callback_data = f"{input_match_hash}_{number_match_db}_{data_currency_capital['currency_id']}"

            button = InlineKeyboardButton(text=str(text), callback_data=callback_data)
            builder.add(button)

        builder.adjust(2)

        if str(builder.as_markup()) != 'inline_keyboard=[]':
            return builder.as_markup()
    else:
        return None


