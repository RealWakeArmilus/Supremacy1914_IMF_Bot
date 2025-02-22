from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def menu_setting_matches() -> InlineKeyboardMarkup:

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('Создать'), callback_data=f'CreatedMatch'))
    builder.add(InlineKeyboardButton(text=str('Удалить'), callback_data=f'DeletedMatch'))
    builder.add(InlineKeyboardButton(text=str('Назад в Личный кабинет'), callback_data=f'StartOpenAccount'))
    builder.adjust(2, 1)

    return builder.as_markup()


async def created_match_step(number_step: int) -> InlineKeyboardMarkup:
    """1 - первый этап (номер), 2 - второй этап (категория), 3 - третий этап (тип карты)"""
    builder = InlineKeyboardBuilder()

    if number_step == 1:
        builder.add(InlineKeyboardButton(text=str('Назад в Настройки матча'), callback_data=f'SettingsMatсhes_back'))
    elif number_step == 2:
        builder.add(InlineKeyboardButton(text=str('Родная'), callback_data=f'CategoryMatch_my'))
        builder.add(InlineKeyboardButton(text=str('Для партнера'), callback_data=f'CategoryMatch_partner'))
        builder.add(InlineKeyboardButton(text=str('Изменить Номер матча'), callback_data=f'CreatedMatch'))
        builder.add(InlineKeyboardButton(text=str('Назад в Настройки матча'), callback_data=f'SettingsMatсhes_back'))
        builder.adjust(2, 1, 1)
    elif number_step == 4:
        builder.add(InlineKeyboardButton(text=str('Великая война: 31'), callback_data=f'TypeMap_ВеликаяВойна'))
        builder.add(InlineKeyboardButton(text=str('Война в огне: 100'), callback_data=f'TypeMap_ВойнаВОгне'))
        builder.add(InlineKeyboardButton(text=str('Назад в Настройки матча'), callback_data=f'SettingsMatсhes_back'))
        builder.adjust(2, 1)
    elif number_step == 5:
        builder.add(InlineKeyboardButton(text=str('Подтвердить запуск'), callback_data=f'confirm_creation'))
        builder.add(InlineKeyboardButton(text=str('Очистить и начать заново'), callback_data=f'restart_creation'))
        builder.add(InlineKeyboardButton(text=str('Назад в Настройки матча'), callback_data=f'SettingsMatсhes_back'))
        builder.adjust(2, 1)

    return builder.as_markup()


# types_match = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='Великая война')],
#     [KeyboardButton(text='Мир в огне')]
#     ],
#     resize_keyboard=True
# )

