from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def now_country_menu(number_match: str, status_emission: bool = False) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('Эмиссия национальной валюты'), callback_data=f'EmissionNationalCurrency_{number_match}'))
    builder.add(InlineKeyboardButton(text=str('Торговля'), callback_data=f'Trading_{number_match}'))
    builder.add(InlineKeyboardButton(text=str('Список лимитных заявок'), callback_data=f'ListLimitedOrders_{number_match}'))

    builder.adjust(1)

    return builder.as_markup()


async def emission_menu(number_match: str, message_id_delete: int = None) -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('✅ Начать'), callback_data=f'StartEmissionNationalCurrency_{number_match}'))
    builder.add(InlineKeyboardButton(text=str('Назад'), callback_data=f'CountryMenu_{number_match}_{message_id_delete}'))

    builder.adjust(1)

    return builder.as_markup()


