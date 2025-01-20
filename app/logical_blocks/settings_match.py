from aiogram import F, Router
from aiogram.types import CallbackQuery

# Import required modules
from app.DatabaseWork.database import DatabaseManager
import app.keyboards.settings_match as kb
from app.utils import callback_utils

router = Router()


@router.callback_query(F.data == 'settings_match')
async def start_settings_match(callback: CallbackQuery):
    """Handle settings match callback."""
    await callback_utils.notify_user(callback, 'Вы перешли в настройки матча.')

    match_numbers = await kb.numbers_match()
    if match_numbers:
        await callback_utils.send_edit_message(
            callback,
            'Выберите номер матча, который желаете настроить',
            await kb.numbers_match('SettingMatch')
        )
    else:
        await callback_utils.send_edit_message(callback, 'На текущий момент список матчей пуст.')


@router.callback_query(lambda c: c.data and c.data.startswith('SettingMatch_'))
async def choice_number_match_for_settings(callback: CallbackQuery):
    """Handle choice of match for settings."""
    number_match = callback_utils.get_number_match_from_callback_data(callback.data, 'SettingMatch')

    await callback_utils.notify_user(callback, f"Вы выбрали матч с номером: {number_match}")

    await callback_utils.send_edit_message(
        callback,
        f"Что желаете сделать с матчем: {number_match}",
        await kb.edit_match(number_match)
    )


@router.callback_query(lambda c: c.data and c.data.startswith('DeleteMatch_'))
async def deleted_match(callback: CallbackQuery):
    """Handle deletion of a match."""
    number_match = callback_utils.get_number_match_from_callback_data(callback.data, 'DeleteMatch')

    success = await DatabaseManager().delete_match(
        number_match=number_match
    )

    response = (
        f"Номер матча {number_match} был успешно удалён."
        if success else
        f"Не удалось удалить номер матча {number_match}. Попробуйте позже."
    )

    await callback_utils.notify_user(callback, response)

    # Restart the settings menu
    await start_settings_match(callback)
