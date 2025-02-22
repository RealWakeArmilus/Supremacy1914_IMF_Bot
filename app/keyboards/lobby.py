from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def main_lobby() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('Личный кабинет'), callback_data=f'StartOpenAccount'))
    builder.add(InlineKeyboardButton(text=str('Сертификаты'), callback_data=f'LobbyCertificates'))
    builder.add(InlineKeyboardButton(text=str('Игровые сессии'), callback_data=f'sessions'))

    builder.adjust(1)
    return builder.as_markup()
