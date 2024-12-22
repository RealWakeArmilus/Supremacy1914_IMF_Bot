from aiogram import Router
from aiogram.types import CallbackQuery

# Импортируйте модули, которые используются внутри функций
import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db
from app.message_designer.deletezer import delete_message
from app.utils import callback_utils

router = Router()


@router.callback_query(lambda c: c.data and c.data.startswith('ConfirmRequestCountryByAdmin_'))
async def confirm_request_country_by_admin(callback: CallbackQuery):

    data_parts = callback_utils.parse_callback_data(callback.data, 'ConfirmRequestCountryByAdmin')
    unique_word, number_match = data_parts[0], data_parts[1]

    await callback_utils.notify_user(callback, 'Решение заявки')

    try:
        # get data user who submitted the application
        data_user = await match_db.get_data_user_for_request(unique_word, number_match)

        await match_db.register_country_in_match(data_user)

        await callback.bot.send_message(chat_id=data_user['telegram_id'],
                                        text=f'<b>Ваша заявка на вход в матч:</b> {number_match}'
                                        '\n<b>Статус:</b> Одобрена'
                                        f'\n<b>Государство:</b> {data_user['name_country']}',
                                        parse_mode="html")

        chat_id_admin = await master_db.get_telegram_id_admin()

        await callback.bot.send_message(chat_id=chat_id_admin,
                                        text=f'<b>Вы одобрили заявку матча:</b> {number_match}'
                                        f'\n<b>Государство:</b> {data_user['name_country']}',
                                        parse_mode="html")

        await delete_message(callback.bot, chat_id_admin, data_user['admin_decision_message_id'])

    except Exception as error:
        await callback_utils.handle_error(callback, error, "Произошла ошибка при подтверждении заявки.")


@router.callback_query(lambda c: c.data and c.data.startswith('RejectRequestCountryByAdmin_'))
async def reject_request_country_by_admin_(callback: CallbackQuery):

    data_parts = callback_utils.parse_callback_data(callback.data, 'RejectRequestCountryByAdmin')
    unique_word, number_match = data_parts[0], data_parts[1]

    await callback_utils.notify_user(callback, 'Решение заявки')

    try:
        # get data user who submitted the request
        data_user = await match_db.get_data_user_for_request(unique_word, number_match)

        # deleted request
        await match_db.deleted_request_country_in_match(data_user)

        await callback.bot.send_message(chat_id=data_user['telegram_id'],
                                        text=f'<b>Ваша заявка на вход в матч:</b> {number_match}'
                                        '\n<b>Статус:</b> Отклонена'
                                        f'\n<b>Государство:</b> {data_user['name_country']}',
                                        parse_mode="html")

        chat_id_admin = await master_db.get_telegram_id_admin()

        await callback.bot.send_message(chat_id=chat_id_admin,
                                        text=f'<b>Вы отклонили заявку матча:</b> {number_match}'
                                        f'\n<b>Государство:</b> {data_user['name_country']}',
                                        parse_mode="html")

        await delete_message(callback.bot, chat_id_admin, data_user['admin_decision_message_id'])

    except Exception as error:
        await callback_utils.handle_error(callback, error, "Произошла ошибка при отклонении заявки.")

