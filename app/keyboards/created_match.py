from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton


types_map = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Великая война')]],
    resize_keyboard=True
)

confirm_created_map = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Подтвердить создание', callback_data='confirm_creation')],
    [InlineKeyboardButton(text='🔄 Начать заново', callback_data='restart_creation')]
])

