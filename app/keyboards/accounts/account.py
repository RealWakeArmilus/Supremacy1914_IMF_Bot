from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class StartMenuAccount:
    def __init__(self):
        self.builder = InlineKeyboardBuilder()

    async def free(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Пригласить друга и получить 50💎'), callback_data=f'ReferralLink'))
        builder.add(InlineKeyboardButton(text=str('Пополнить баланс на 150💎'), callback_data=f'UpBalance'))
        builder.add(InlineKeyboardButton(text=str('Активировать Premium'), callback_data=f'BecomePremium'))
        builder.add(InlineKeyboardButton(text=str('Приобрести Premium'), callback_data=f'BecomePremium'))
        builder.add(InlineKeyboardButton(text=str('Стать Partner'), callback_data=f'BecomePartner'))
        builder.add(InlineKeyboardButton(text=str('Назад в меню'), callback_data=f'menu'))
        builder.adjust(1, 1, 2, 1, 1)
        return builder.as_markup()

    async def partner(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Пригласить друга и получить 50💎'), callback_data=f'ReferralLink'))
        builder.add(InlineKeyboardButton(text=str('Пополнить баланс на 150💎'), callback_data=f'UpBalance'))
        builder.add(InlineKeyboardButton(text=str('Настройка ваших матчей'), callback_data=f'SettingsPartnerMatсhes'))
        builder.add(InlineKeyboardButton(text=str('Приобрести Premium'), callback_data=f'BecomePremium'))
        builder.add(InlineKeyboardButton(text=str('Назад в меню'), callback_data=f'menu'))
        builder.adjust(1)
        return builder.as_markup()

    async def admin(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Пригласить друга и получить 50💎'), callback_data=f'ReferralLink'))
        builder.add(InlineKeyboardButton(text=str('Пополнить баланс на 150💎'), callback_data=f'UpBalance'))
        builder.add(InlineKeyboardButton(text=str('Balance Everyone 💎'), callback_data=f'BalanceAccounts'))
        builder.add(InlineKeyboardButton(text=str('Premiums'), callback_data=f'BalanceAccounts'))
        builder.add(InlineKeyboardButton(text=str('Матчи Partners'), callback_data=f'MatсhesPartner'))
        builder.add(InlineKeyboardButton(text=str('Приобрести Premium'), callback_data=f'BecomePremium'))
        builder.add(InlineKeyboardButton(text=str('Назад в меню'), callback_data=f'menu'))
        builder.adjust(1, 1, 1, 2, 1, 1)
        return builder.as_markup()

    async def owner(self) -> InlineKeyboardMarkup:
        builder = self.builder
        builder.add(InlineKeyboardButton(text=str('Настройки Матча'), callback_data=f'SettingsMatсhes_None'))
        builder.add(InlineKeyboardButton(text=str('Balance Everyone 💎'), callback_data=f'BalanceAccounts'))
        builder.add(InlineKeyboardButton(text=str('Premiums'), callback_data=f'BalanceAccounts'))
        builder.add(InlineKeyboardButton(text=str('Матчи Partners'), callback_data=f'MatсhesPartner'))
        builder.add(InlineKeyboardButton(text=str('Admins'), callback_data=f'AdminAccounts'))
        builder.add(InlineKeyboardButton(text=str('Назад в меню'), callback_data=f'menu'))
        builder.adjust(1, 2, 2, 1)
        return builder.as_markup()
