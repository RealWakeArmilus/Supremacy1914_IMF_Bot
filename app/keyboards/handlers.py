from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать матч', callback_data='created_match')],
    [InlineKeyboardButton(text='Настройки существующих матчей', callback_data='settings_match')]
])






