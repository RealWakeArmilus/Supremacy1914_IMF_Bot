from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def main_lobby() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='Личный кабинет', callback_data='StartOpenAccount'))
    builder.add(InlineKeyboardButton(text='Сертификаты', web_app=WebAppInfo(url="https://realwakearmilus.github.io/resume/")))
    builder.add(InlineKeyboardButton(text='Игровые сессии', callback_data='sessions'))

    builder.adjust(1)
    return builder.as_markup()
