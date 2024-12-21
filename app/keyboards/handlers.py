from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db

from app.message_designer.hashzer import hash_callback_suffix_64_name_state


admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Создать карту', callback_data='created_match')],
    [InlineKeyboardButton(text='Настройки существующих карт', callback_data='settings_match')]
])






