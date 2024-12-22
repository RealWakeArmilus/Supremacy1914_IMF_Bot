from asyncio.log import logger

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

# Импортируйте модули, которые используются внутри функций
import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db

# import keyboards
import app.keyboards.choice_state as kb

from aiogram import Router

from app.message_designer.deletezer import delete_message

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith('ConfirmRequestStateByAdmin_'))
async def confirm_request_state_by_admin(callback: CallbackQuery):

    unique_word = callback.data.split('_')[1]
    number_match = callback.data.split('_')[2]

    await callback.answer('Решение заявки')

    try:
        # get data user who submitted the application
        data_user = await match_db.get_data_user_for_request(unique_word, number_match)

        await match_db.register_state_in_match(data_user)

        await callback.bot.send_message(chat_id=data_user['telegram_id'],
                                        text=f'<b>Ваша заявка на вход в матч:</b> {number_match}'
                                        '\n<b>Статус:</b> Одобрена'
                                        f'\n<b>Государство:</b> {data_user['name_state']}',
                                        parse_mode="html")

        chat_id_admin = await master_db.get_telegram_id_admin()

        await callback.bot.send_message(chat_id=chat_id_admin,
                                        text=f'<b>Вы одобрили заявку матча:</b> {number_match}'
                                        f'\n<b>Государство:</b> {data_user['name_state']}',
                                        parse_mode="html")

        await delete_message(callback.bot, chat_id_admin, data_user['admin_decision_message_id'])

    except Exception as error:
        logger.error(f"Ошибка при подтверждении заявки: {error}")
        await callback.answer("Произошла ошибка при подтверждении заявки.")


@router.callback_query(lambda c: c.data and c.data.startswith('RejectRequestStateByAdmin_'))
async def reject_request_state_by_admin_(callback: CallbackQuery):

    unique_word = callback.data.split('_')[1]
    number_match = callback.data.split('_')[2]

    await callback.answer('Решение заявки')

    try:
        # get data user who submitted the request
        data_user = await match_db.get_data_user_for_request(unique_word, number_match)

        # deleted request
        await match_db.deleted_request_state_in_match(data_user)

        await callback.bot.send_message(chat_id=data_user['telegram_id'],
                                        text=f'<b>Ваша заявка на вход в матч:</b> {number_match}'
                                        '\n<b>Статус:</b> Отклонена'
                                        f'\n<b>Государство:</b> {data_user['name_state']}',
                                        parse_mode="html")

        chat_id_admin = await master_db.get_telegram_id_admin()

        await callback.bot.send_message(chat_id=chat_id_admin,
                                        text=f'<b>Вы отклонили заявку матча:</b> {number_match}'
                                        f'\n<b>Государство:</b> {data_user['name_state']}',
                                        parse_mode="html")

        await delete_message(callback.bot, chat_id_admin, data_user['admin_decision_message_id'])

    except Exception as error:
        logger.error(f"Ошибка при отклонении заявки: {error}")
        await callback.answer("Произошла ошибка при отклонении заявки.")

