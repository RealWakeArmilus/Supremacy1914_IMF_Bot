from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def main_lobby() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text='Личный кабинет', callback_data='StartOpenAccount'))
    builder.add(InlineKeyboardButton(text='IMF-SPACE', web_app=WebAppInfo(url="https://realwakearmilus.github.io/Supremacy1914_IMF_Bot/")))

    builder.adjust(1)
    return builder.as_markup()
