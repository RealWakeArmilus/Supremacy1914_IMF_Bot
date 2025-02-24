from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

# Import required modules
from app.decorators.message import MessageManager
from app.DatabaseWork.models_master import CertificatesManager

logger = logging.getLogger(__name__)
certificates_manager = CertificatesManager()

router = Router()

PREFIXES = {
    "LOBBY": "LobbyCertificates"
}


@router.callback_query(F.data == f'{PREFIXES['LOBBY']}')
async def lobby_certificates(callback: CallbackQuery, state: FSMContext):
    """Отрытие лобби сертификатов пользователя"""
    logger.info('📶get_certificates from "lobby_certificates": connect')

    get_certificates_task = certificates_manager.get_certificates(telegram_id=callback.from_user.id)
    message_manager = MessageManager(bot=callback.bot, state=state)

    certificates_user = await get_certificates_task

    if certificates_user is None:
        await message_manager.send_photo(
            obj=callback,
            text='Ваши данные мне не доступны.',
            remove_previous=True,
            clear_state_photo_message_id=True
        )
        return

    text = (
        f'<b>Базовый №1:</b> {'True' if certificates_user['base_one'] else 'False'}\n'
        f'<b>Базовый №2:</b> {'True' if certificates_user['base_two'] else 'False'}\n'
        f'<b>Базовый №3:</b> {'True' if certificates_user['base_three'] else 'False'}'
    )

    await message_manager.send_photo(
        obj=callback,
        text=text,
        remove_previous=True
    )
