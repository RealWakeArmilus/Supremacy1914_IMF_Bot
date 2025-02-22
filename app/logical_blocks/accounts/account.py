from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

# Import required modules
from app.decorators.message import MessageManager
from app.DatabaseWork.models_master import UserManager
import app.keyboards.accounts.account as kb

logger = logging.getLogger(__name__)

router = Router()
user_manager = UserManager()

# Callback prefixes
PREFIXES = {
    "START": "StartOpenAccount"
}


@router.callback_query(F.data == f'{PREFIXES['START']}')
async def start_open_account(callback: CallbackQuery, state: FSMContext):
    """Отрытие личного кабинета"""
    logger.info('📶get_user from "start_open_account": connect')

    get_user_task = user_manager.get_user(telegram_id=callback.from_user.id)
    message_manager = MessageManager(bot=callback.bot, state=state)

    data_user = await get_user_task

    if data_user is None:
        await message_manager.send_photo(
            obj=callback,
            text='Ваши данные мне не доступны.',
            remove_previous=True,
            clear_state_photo_message_id=True
        )
        return

    if data_user['is_free']:
        keyboard_task = kb.StartMenuAccount().free()
        status = 'Free'
        count_premium = data_user['count_premium']
    elif data_user['is_premium']:
        keyboard_task = kb.StartMenuAccount().premium()
        status = 'Premium'
        count_premium = data_user['count_premium']
    elif data_user['is_partner']:
        keyboard_task = kb.StartMenuAccount().partner()
        status = 'Partner'
        count_premium = data_user['count_premium']
    elif data_user['is_admin']:
        keyboard_task = kb.StartMenuAccount().admin()
        status = 'Admin'
        count_premium = data_user['count_premium']
    elif data_user['is_owner']:
        keyboard_task = kb.StartMenuAccount().owner()
        status = 'Owner'
        count_premium = data_user['count_premium']
    else:
        keyboard_task = None
        status = '???'
        count_premium = 0

    keyboard = await keyboard_task

    photo_path = 'image/Price_list_bot.png'
    text = (
        '<b>Ваш баланс:</b> 0 💎\n'
        f'<b>Ваш статус:</b> {status}\n\n'
        f'<b>Premium в запасе:</b> {count_premium}\n\n'
        '<b>Чтобы вернуться к меню введите: /menu</b>'
    )

    await message_manager.send_photo(
        obj=callback,
        text=text,
        photo_path=photo_path,
        keyboard=keyboard,
        remove_previous=True
    )



