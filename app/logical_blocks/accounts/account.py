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
        status = 'Free'
        keyboard_task = kb.StartMenuAccount().free()
    elif data_user['is_partner']:
        keyboard_task = kb.StartMenuAccount().partner()
        status = 'Partner'
    elif data_user['is_admin']:
        keyboard_task = kb.StartMenuAccount().admin()
        status = 'Admin'
    elif data_user['is_owner']:
        keyboard_task = kb.StartMenuAccount().owner()
        status = 'Owner - v. 0.2.2.4'
    else:
        keyboard_task = None
        status = '???'

    if data_user['is_premium']:
        premium = f'<b>Активирован до:</b> {data_user["end_premium"]}'
    else:
        premium = '<b>Не активирован:</b> -'

    count_premium = data_user['count_premium']

    if keyboard_task:
        keyboard = await keyboard_task
    else:
        keyboard = None

    photo_path = 'image/Price_list_bot.png'
    text = (
        '<b>Ваш баланс:</b> 0 💎\n'
        f'<b>Ваш статус:</b> {status}\n\n'
        '<i>Информация по Premium:</i>\n'
        f'{premium}\n'
        f'<b>Premium в запасе:</b> {count_premium}'
    )

    await message_manager.send_photo(
        obj=callback,
        text=text,
        photo_path=photo_path,
        keyboard=keyboard,
        remove_previous=True
    )



