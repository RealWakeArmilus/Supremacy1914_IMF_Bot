from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.DatabaseWork.master as master_db


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


async def numbers_match() -> InlineKeyboardMarkup | None:

    numbers = await master_db.get_numbers_match()

    if numbers:

        builder = InlineKeyboardBuilder()

        for number in numbers:
            button = InlineKeyboardButton(text=str(number), callback_data=f"match_{number}")
            builder.add(button)

        builder.adjust(3)

        return builder.as_markup()

    else:
        return None


async def edit_match(number_match: str) -> InlineKeyboardMarkup:
    delete_button = InlineKeyboardButton(text="Удалить", callback_data=f"delete_{number_match}")
    return InlineKeyboardMarkup(inline_keyboard=[[delete_button]])
