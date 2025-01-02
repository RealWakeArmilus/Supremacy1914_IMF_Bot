from aiogram import Router
from aiogram.types import CallbackQuery

# Импортируйте модули, которые используются внутри функций
import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db
from app.message_designer.deletezer import delete_message
from app.utils import callback_utils

router = Router()


async def result_of_admin_decision_for_request_choice_country(callback: CallbackQuery, number_match: str, data_request: dict, decision: bool = False):
    """
    Показывает решение админа на заявку. Отправляет в чат пользователю и админу решение по заявке

    :param number_match: number match
    :param callback: CallbackQuery
    :param data_request: await match_db.get_data_country_choice_request(unique_word, number_match)
    :param decision: True - одобрено, False - отклонено
    """
    telegram_id = data_request['telegram_id']
    name_country = data_request['name_country']
    admin_decision_message_id = data_request['admin_decision_message_id']


    message_decision = (
        'Одобрили'
        if decision else
        'Отклонили')

    await callback_utils.notify_user(callback, 'Решение заявки')

    await callback.bot.send_message(chat_id=telegram_id,
                                    text=f'<b>Ваша заявка на вход в матч:</b> {number_match}'
                                         f'\n<b>Статус:</b> {message_decision}'
                                         f'\n<b>Государство:</b> {name_country}',
                                    parse_mode="html")

    chat_id_admin = await master_db.get_telegram_id_admin()

    await callback.bot.send_message(chat_id=chat_id_admin,
                                    text=f'<b>Вы {message_decision} заявку матча:</b> {number_match}'
                                         f'\n<b>Государство:</b> {name_country}',
                                    parse_mode="html")

    await delete_message(callback.bot, chat_id_admin, admin_decision_message_id)


@router.callback_query(lambda c: c.data and c.data.startswith('ConfirmRequestCountryByAdmin_'))
async def confirm_request_country_by_admin(callback: CallbackQuery):

    data_parts = callback_utils.parse_callback_data(callback.data, 'ConfirmRequestCountryByAdmin')
    unique_word, number_match = data_parts[0], data_parts[1]

    try:
        # get data user who submitted the application
        data_user = await match_db.get_data_country_choice_request(unique_word, number_match)

        await match_db.register_country_in_match(data_user)

        await result_of_admin_decision_for_request_choice_country(callback, number_match, data_user, True)
    except Exception as error:
        await callback_utils.handle_error(callback, error, "Произошла ошибка при подтверждении заявки.")


@router.callback_query(lambda c: c.data and c.data.startswith('RejectRequestCountryByAdmin_'))
async def reject_request_country_by_admin_(callback: CallbackQuery):

    data_parts = callback_utils.parse_callback_data(callback.data, 'RejectRequestCountryByAdmin')
    unique_word, number_match = data_parts[0], data_parts[1]

    await callback_utils.notify_user(callback, 'Решение заявки')

    try:
        # get data user who submitted the request
        data_user = await match_db.get_data_country_choice_request(unique_word, number_match)

        # deleted request
        await match_db.deleted_request_country_in_match(data_user)

        await result_of_admin_decision_for_request_choice_country(callback, number_match, data_user)
    except Exception as error:
        await callback_utils.handle_error(callback, error, "Произошла ошибка при отклонении заявки.")

