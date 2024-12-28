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


async def choice_amount_emission_national_currency(number_match: str) -> InlineKeyboardMarkup | None:
    """
    :param number_match: number match
    :return: InlineKeyboardMarkup | None
    """
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('5.000.000.000 (пять миллиардов) единиц.'), callback_data=f'AmountEmissionNatCurrency_{number_match}_5billions'))
    builder.add(InlineKeyboardButton(text=str('10.000.000.000 (десять миллиардов) единиц.'), callback_data=f'AmountEmissionNatCurrency_{number_match}_10billions'))

    builder.adjust(1)

    return builder.as_markup()


async def end_emission_national_currency(number_match: str) -> InlineKeyboardMarkup | None:
    """
    :param number_match: number match
    :return: InlineKeyboardMarkup | None
    """

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('✅ Подтвердить запуск'), callback_data='ConfirmFormEmissionNatCurrency'))
    builder.add(InlineKeyboardButton(text=str('🔄 Начать заново'), callback_data=f'RestartFormEmissionNatCurrency_{number_match}'))

    builder.adjust(1)

    return builder.as_markup()


async def verify_form_emission_national_currency(number_match: str):
    """
    Create keyboards from verify form emission national currency by admin
    :param number_match:
    """

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text=str('✅ Подтвердить'), callback_data=f'ConfirmRequestFormEmisNatCur_{number_match}'))
    builder.add(InlineKeyboardButton(text=str('❌ Отклонить'), callback_data=f'RejectRequestFormEmisNatCur_{number_match}'))

    builder.adjust(1)

    return builder.as_markup()

