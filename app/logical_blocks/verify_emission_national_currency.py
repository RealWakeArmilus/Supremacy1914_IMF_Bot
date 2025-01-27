from aiogram import Router
from aiogram.types import CallbackQuery

# Импортируйте модули, которые используются внутри функций
# import app.DatabaseWork.match as match_db
from app.DatabaseWork.database import DatabaseManager
from app.message_designer.deletezer import delete_message
from app.utils import callback_utils


# Router setup
router = Router()


async def result_of_admin_decision_for_request_emis_nat_currency(callback: CallbackQuery, number_match: str, telegram_id_user: int, data_request: dict, decision: bool = False):
    """
    Показывает решение админа на заявку. Отправляет в чат пользователю и админу решение по заявке

    :param number_match: номер матча
    :param telegram_id_user: номер пользователя который создал заявку
    :param callback: CallbackQuery
    :param data_request: await match_db.get_data_form_emis_nat_currency_request(callback.from_user.id, number_match)
    :param decision: True - одобрено, False - отклонено
    """
    id_request = data_request['id']
    data_country = await DatabaseManager(database_path=number_match).get_data_country(user_id=telegram_id_user, number_match=number_match)
    name_currency = data_request['name_currency']
    tick_currency = data_request['tick_currency']
    following_resource = data_request['following_resource']
    course_following = data_request['course_following']
    amount_emission_currency = data_request['amount_emission_currency']
    capitalization = data_request['capitalization']


    message_decision = (
        'Одобрили'
        if decision else
        'Отклонили')

    await callback_utils.notify_user(callback, 'Решение заявки')

    await callback.bot.send_message(chat_id=data_request['telegram_id'],
                                    text=f'<b>Ваша заявка #{id_request}, на эмиссию валюты:</b> {name_currency}'
                                         f'\n<b>Статус:</b> {message_decision}'
                                         '<blockquote>'
                                         f"<b>Матч:</b> {number_match}\n"
                                         f"<b>Государство:</b> {data_country['name_country']}\n"
                                         f"<b>Название валюты:</b> {name_currency}\n"
                                         f"<b>Тикер валюты:</b> {tick_currency}\n"
                                         f"<b>Валюта закреплена за ресурсом:</b> {following_resource}\n"
                                         f"<b>Соотношение валюты к ресурсу:</b> {course_following} ед. к 1 {following_resource}\n"
                                         f"<b>Объем эмиссии:</b> {amount_emission_currency} единиц\n"
                                         f"<b>Капитализация:</b> {capitalization} серебра"
                                         '</blockquote>',
                                    parse_mode="html")

    chat_id_admin = await DatabaseManager().get_owner_admin_telegram_id()

    await callback.bot.send_message(chat_id=chat_id_admin,
                                    text=f'<b>Вы {message_decision} заявку #{id_request}, на эмиссию валюты:</b> {name_currency}'
                                         '<blockquote>'
                                         f"<b>Матч:</b> {number_match}\n"
                                         f"<b>Государство:</b> {data_country['name_country']}\n"
                                         f"<b>Название валюты:</b> {name_currency}\n"
                                         f"<b>Тикер валюты:</b> {tick_currency}\n"
                                         f"<b>Валюта закреплена за ресурсом:</b> {following_resource}\n"
                                         f"<b>Соотношение валюты к ресурсу:</b> {course_following} ед. к 1 {following_resource}\n"
                                         f"<b>Объем эмиссии:</b> {amount_emission_currency} единиц\n"
                                         f"<b>Капитализация:</b> {capitalization} серебра"
                                         '</blockquote>',
                                    parse_mode="html")


@router.callback_query(lambda c: c.data and c.data.startswith('ConfirmRequestFormEmisNatCur_'))
async def confirm_request_form_emis_nat_currency_by_admin(callback: CallbackQuery):
    """
    Решение админа - ОДОБРЕНА заявка на эмиссию валюты

    :param callback:
    """

    number_match = callback_utils.parse_callback_data(callback.data, 'ConfirmRequestFormEmisNatCur')[0]
    telegram_id_user = int(callback_utils.parse_callback_data(callback.data, 'ConfirmRequestFormEmisNatCur')[1])

    try:
        # get data user who submitted the application
        # data_request = await match_db.get_data_form_emis_nat_currency_request(callback.from_user.id, number_match)
        data_request = await DatabaseManager(database_path=number_match).get_data_form_emis_nat_currency_request(user_id=telegram_id_user)

        await DatabaseManager(database_path=number_match).register_currency_emission_in_match(
            data_request=data_request
        )
        await DatabaseManager(database_path=number_match).set_national_currency_in_currency_capitals(
            user_id=telegram_id_user,
            number_match=number_match,
        )

        chat_id_admin = await DatabaseManager().get_owner_admin_telegram_id()

        await delete_message(callback.bot, chat_id_admin, data_request['message_id_delete'])

        await result_of_admin_decision_for_request_emis_nat_currency(callback, number_match, telegram_id_user, data_request, True)
    except Exception as error:
        await callback_utils.handle_exception(callback, 'confirm_request_form_emis_nat_currency_by_admin', error, "Произошла ошибка при подтверждении заявки.")


@router.callback_query(lambda c: c.data and c.data.startswith('RejectRequestFormEmisNatCur_'))
async def reject_request_form_emis_nat_currency_by_admin(callback: CallbackQuery):

    number_match = callback_utils.parse_callback_data(callback.data, 'RejectRequestFormEmisNatCur')[0]
    telegram_id_user = int(callback_utils.parse_callback_data(callback.data, 'RejectRequestFormEmisNatCur')[1])

    try:
        # get data user who submitted the application
        # data_request = await match_db.get_data_form_emis_nat_currency_request(callback.from_user.id, number_match)
        data_request = await DatabaseManager(database_path=number_match).get_data_form_emis_nat_currency_request(user_id=telegram_id_user)

        await DatabaseManager(database_path=number_match).register_currency_emission_in_match(data_request=data_request, result_verify=False)

        await result_of_admin_decision_for_request_emis_nat_currency(callback, number_match, telegram_id_user, data_request)
    except Exception as error:
        await callback_utils.handle_exception(callback, 'reject_request_form_emis_nat_currency_by_admin', error, "Произошла ошибка при отклонении заявки.")

