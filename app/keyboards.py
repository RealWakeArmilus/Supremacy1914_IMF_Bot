from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton


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

