from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton


types_match = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Великая война')]],
    resize_keyboard=True
)

confirm_created_match = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Подтвердить создание', callback_data='confirm_creation')],
    [InlineKeyboardButton(text='🔄 Начать заново', callback_data='restart_creation')]
])

