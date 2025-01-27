from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def now_country_menu(number_match: str, status_emission: bool = False) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    if status_emission is False:
        builder.add(InlineKeyboardButton(text=str('Эмиссия национальной валюты'), callback_data=f'EmissionNationalCurrency_{number_match}'))
    elif status_emission:
        builder.add(InlineKeyboardButton(text=str('Банковские переводы'), callback_data=f'BankTransfer_{number_match}'))
        builder.add(InlineKeyboardButton(text=str('Пожаловаться'), callback_data=f'Complain_{number_match}'))

    builder.adjust(1)

    return builder.as_markup()


async def lobby_emission_nat_currency_menu(number_match: str, message_id_delete: int = None) -> InlineKeyboardMarkup:
    """
    :param number_match:
    :param message_id_delete:
    :return: меню для лобби эмиссии нац валюты
    """
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('✅ Начать'), callback_data=f'StartEmissionNationalCurrency_{number_match}'))
    builder.add(InlineKeyboardButton(text=str('Назад'), callback_data=f'CountryMenu_{number_match}_{message_id_delete}'))

    builder.adjust(1)

    return builder.as_markup()


async def lobby_bank_transfer_menu(number_match: str, message_id_delete: int = None) -> InlineKeyboardMarkup:
    """
    :param number_match:
    :param message_id_delete:
    :return: меню для лобби банковских переводов
    """
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('✅ Начать'), callback_data=f'StartBankTransfer_{number_match}'))
    builder.add(InlineKeyboardButton(text=str('Назад'), callback_data=f'CountryMenu_{number_match}_{message_id_delete}'))

    builder.adjust(1)

    return builder.as_markup()


