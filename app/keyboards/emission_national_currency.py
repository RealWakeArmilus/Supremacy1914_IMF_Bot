from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def choice_following_resource_national_currency(number_match: str) -> InlineKeyboardMarkup | None:
    """
    :param number_match: number match
    :return: InlineKeyboardMarkup | None
    """
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('Серебро (Silver)'), callback_data=f'FollowingResourceNatCurrency_{number_match}_silver'))

    builder.adjust(1)

    return builder.as_markup()

