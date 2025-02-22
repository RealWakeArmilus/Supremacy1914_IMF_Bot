from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class StartMenuAccount:
    def __init__(self):
        self.builder = InlineKeyboardBuilder()

    async def free(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Пригласить друга и получить 50💎'), callback_data=f'ReferralLink'))
        builder.add(InlineKeyboardButton(text=str('Пополнить баланс на 150💎'), callback_data=f'UpBalance'))
        builder.add(InlineKeyboardButton(text=str('Стать Premium'), callback_data=f'BecomePremium'))
        builder.add(InlineKeyboardButton(text=str('Стать Partner'), callback_data=f'BecomePartner'))
        builder.adjust(1)
        return builder.as_markup()

    async def premium(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Пригласить друга и получить 50💎'), callback_data=f'ReferralLink'))
        builder.add(InlineKeyboardButton(text=str('Пополнить баланс на 150💎'), callback_data=f'UpBalance'))
        builder.add(InlineKeyboardButton(text=str('Стать Partner'), callback_data=f'BecomePartner'))
        builder.adjust(1)
        return builder.as_markup()

    async def partner(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Пригласить друга и получить 50💎'), callback_data=f'ReferralLink'))
        builder.add(InlineKeyboardButton(text=str('Пополнить баланс на 150💎'), callback_data=f'UpBalance'))
        builder.add(InlineKeyboardButton(text=str('Настройка ваших матчей'), callback_data=f'SettingsPartnerMatсhes'))
        builder.adjust(1)
        return builder.as_markup()

    async def admin(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Пригласить друга и получить 50💎'), callback_data=f'ReferralLink'))
        builder.add(InlineKeyboardButton(text=str('Пополнить баланс на 150💎'), callback_data=f'UpBalance'))
        builder.add(InlineKeyboardButton(text=str('Балансы пользователей'), callback_data=f'BalanceAccounts'))
        builder.add(InlineKeyboardButton(text=str('Матчи партнеров'), callback_data=f'MatсhesPartner'))
        builder.adjust(1)
        return builder.as_markup()

    async def owner(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Настройки Матча'), callback_data=f'SettingsMatсhes_None'))
        builder.add(InlineKeyboardButton(text=str('Балансы пользователей'), callback_data=f'BalanceAccounts'))
        builder.add(InlineKeyboardButton(text=str('Матчи партнеров'), callback_data=f'MatсhesPartner'))
        builder.add(InlineKeyboardButton(text=str('Админы'), callback_data=f'AdminAccounts'))
        builder.adjust(1)
        return builder.as_markup()
