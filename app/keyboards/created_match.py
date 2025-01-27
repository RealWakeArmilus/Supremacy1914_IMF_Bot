from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton

#TODO замени keyboard на inline

# async def types_match() -> InlineKeyboardMarkup | None:
#
#     builder = InlineKeyboardBuilder()
#
#     builder.add(InlineKeyboardButton(text=str('Великая война'), callback_data='great_war'))
#
#     builder.adjust(1)
#
#     return builder.as_markup()

types_match = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Великая война')],
    [KeyboardButton(text='Мир в огне')]
    ],
    resize_keyboard=True
)

