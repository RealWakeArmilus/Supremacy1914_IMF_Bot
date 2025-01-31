from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



async def launch_solution(
        launch_type: str,
        number_match: str = None
) -> InlineKeyboardMarkup | None:
    """
    Создаёт инлайн клавиатуру для подтверждения запуска процесса или перезапуска процесса для его начала заново

    :param launch_type: тип процесса
    :param number_match:
    :return: Объект InlineKeyboardMarkup с кнопками "Подтвердить запуск" и "Начать заново".
    """
    try:
        builder = InlineKeyboardBuilder()

        if launch_type == 'creation': # created_match
            confirm_callback = f'confirm_{launch_type}'
            restart_callback = f'restart_{launch_type}'
        elif number_match and (launch_type == 'FormEmissionNatCurrency'):
            confirm_callback = f'Confirm{launch_type}'
            restart_callback = f'Restart{launch_type}_{number_match}'
        elif number_match and (launch_type == 'FormBankTransfer'):
            confirm_callback = f'Confirm{launch_type}'
            restart_callback = f'Restart{launch_type}_{number_match}'
        else:
            raise Exception('Невозможно создать клавиатуру "result - else".')

        builder.add(
            InlineKeyboardButton(text='✅ Подтвердить запуск', callback_data=confirm_callback),
            InlineKeyboardButton(text='🔄 Начать заново', callback_data=restart_callback)
        )

        builder.adjust(1)

        return builder.as_markup()
    except Exception as error:
        print(f'Ошибка клавиатуры app.keyboards.universal.launch_solution: {error}')
        return None


async def verify_request_by_admin(
        request_type: str,
        number_match: str,
        unique_word: Optional[str] = None,
        telegram_id_user: Optional[int] = None
) -> InlineKeyboardMarkup | None:
    """
    Создаёт инлайн клавиатуру для подтверждения или отклонения действия администратором.

    :param telegram_id_user: Телеграм id пользователя, который создал заявку
    :param request_type: Тип заявки, например, 'RequestCountryByAdmin' или 'RequestFormEmisNatCur'.
    :param number_match: Номер матча.
    :param unique_word: (Опционально) Уникальное слово, если требуется.
    :return: Объект InlineKeyboardMarkup с кнопками подтверждения и отклонения.
    """
    try:
        builder = InlineKeyboardBuilder()

        if unique_word and (request_type == 'RequestCountryByAdmin'):
            confirm_callback = f'Confirm{request_type}_{unique_word}_{number_match}'
            reject_callback = f'Reject{request_type}_{unique_word}_{number_match}'
        elif request_type == 'RequestFormEmisNatCur':
            confirm_callback = f'Confirm{request_type}_{number_match}_{telegram_id_user}'
            reject_callback = f'Reject{request_type}_{number_match}_{telegram_id_user}'
        else:
            raise Exception('Невозможно создать клавиатуру "result - else".')

        builder.add(
            InlineKeyboardButton(text='✅ Подтвердить заявку', callback_data=confirm_callback),
            InlineKeyboardButton(text='❌ Отклонить заявку', callback_data=reject_callback)
        )

        builder.adjust(1)

        return builder.as_markup()
    except Exception as error:
        print(f'Ошибка клавиатуры app.keyboards.universal.verify_request_by_admin: {error}')
        return None
