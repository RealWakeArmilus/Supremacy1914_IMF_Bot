from aiogram import Router
from aiogram.types import CallbackQuery

# import keyboards
from app.DatabaseWork.database import DatabaseManager
import app.keyboards.country_menu as kb
from app.message_designer.deletezer import delete_message
from app.utils import callback_utils

# Router setup
router = Router()

# import routers from logical_blocks
from app.logical_blocks.emission_national_currency import router as emission_national_currency_router

# connect routers from logical_blocks
router.include_router(emission_national_currency_router)


COUNTRY_MENU = "CountryMenu"
EMISSION_NATIONAL_CURRENCY = "EmissionNationalCurrency"


@router.callback_query(lambda c: c.data and c.data.startswith(f'{COUNTRY_MENU}_'))
async def start_country_menu(callback: CallbackQuery, number_match: str = None):
    """
    Main menu Country

    :param callback: CallbackQuery
    :param number_match: number match | CountryManu_{number_match}_{message_id_delete}
    """
    if number_match is None:
        try:
            number_match = number_match or callback_utils.parse_callback_data(callback.data, COUNTRY_MENU)[0]
            parse_message_id_delete = callback_utils.parse_callback_data(callback.data, COUNTRY_MENU)[1]
            await delete_message(callback.bot, callback.message.chat.id, parse_message_id_delete)
        except (IndexError, TypeError) as error:
            await callback_utils.handle_error(callback, error, 'Ошибка при разборе данных:')
            return

    data_country = await DatabaseManager(database_path=number_match).get_data_country(user_id=callback.from_user.id, number_match=number_match)
    characteristics_country = await DatabaseManager(database_path=number_match).get_data_currency(data_country=data_country, number_match=number_match)

    print(f'data_country: {data_country}'
          f'\ncharacteristics_country: {characteristics_country}')

    currency_info : str = ''

    try:
        currency_info = (
            "не создана (...)"
            if characteristics_country['currency'][0] is False else
            f"{characteristics_country['currency'][0]['name']} ({characteristics_country['currency'][0]['tick']})"
        )
    except Exception as error:
        await callback_utils.handle_error(callback, error, 'Ошибка при выводе информации валюты государства в главном меню государства')

    try:
        if characteristics_country:
            characteristics = (
                f'<b>№ Матча:</b> {number_match}\n'
                f'<b>Ваше Государство:</b> {characteristics_country['name_country']}\n'
                f'<b>Валюта:</b> {currency_info}'
            )

            await callback_utils.send_message(callback,
                                              characteristics,
                                              await kb.now_country_menu(number_match, characteristics_country['currency'][0]))

        elif characteristics_country is None:
            raise Exception(f'Данные пользователя по матчу {number_match} не найдены.')
        else:
            raise Exception(f'Неизвестная ошибка при обработке данных пользователя по матчу {number_match}')
    except Exception as error:
        await callback_utils.handle_error(callback, error, 'Ошибка при выводе данных о государстве в главном меню государства')


@router.callback_query(lambda c: c.data and c.data.startswith(f'{EMISSION_NATIONAL_CURRENCY}_'))
async def emission_national_currency(callback: CallbackQuery):

    number_match = callback_utils.parse_callback_data(callback.data, EMISSION_NATIONAL_CURRENCY)[0]
    message_id = callback.message.message_id

    await callback_utils.notify_user(callback, 'Вы выбрали раздел "эмиссия национальной валюты"')

    if not number_match:
        await callback_utils.handle_error(callback, ValueError("Отсутствует номер матча."), 'Некорректные данные.')
        return

    if message_id is None:
        await callback_utils.handle_error(callback, ValueError("Идентификатор сообщения отсутствует."),'Не удалось получить сообщение.')
        return

    try:
        keyboard = await kb.emission_menu(number_match, message_id)
        await callback_utils.send_edit_message(callback,
                                               '<b>Национальная валюта:</b>\n'
                                               '<pre>'
                                               'Это платежное средство вашего государства. Благодаря ему вы можете покупать/продавать серебро, ресурсы и даже валюты других стран.'
                                               '</pre>\n\n'
                                               '<b>Эмиссия национальной валюты:</b>\n'
                                               '<pre>'
                                               'Это выпуск центральным банком вашего государства новых денежных средств, влияющий на инфляцию и экономическую политику вашей страны.'
                                               '</pre>\n\n'
                                               '<b>Стартовая эмиссия:</b>\n'
                                               '<pre>'
                                               'Это самый первый выпуск ваших денежных единиц. Когда вы вводите свою валюту в обращение.'
                                               '</pre>\n\n'
                                               '<b>Основные моменты, связанные со стартовой эмиссией:</b>\n'
                                               '<pre>'
                                               '1. Название вашей валюты\n\n'
                                               '2. Тикер: трехзначное сокращенное название вашей валюты, для более быстрого и понятного поиска.\n\n'
                                               '3. Капитализация: это общий объем обращающейся вашей валюты в международных резервах и на валютных рынках. Это количество позволяет оценить ликвидность и значимость валюты в мировом экономическом масштабе.\n\n'
                                               '4. Монетарная политика: когда вы устанавливаете политику и регулируете количество выпущенных денег, таким образом, инфляцию и поддерживая стабильность новой валюты.\n\n'
                                               '5. Распространение: вы должны осуществляться торговлю, частью вашего капитала нац. валюты, чтобы дать другим государствам инвестировать в вашу экономику имея вашу валюту как инвестиционный инструмент. \n\nТакой прием работает в обе стороны, вы тоже можете покупать валюты других стран, для спекуляций или инвестирования в чужую экономику.\n\n'
                                               '6. Обеспечение Доверия: чем стабильнее ваша политика с соседним государствами, чем больше ресурсов, серебра и валют других стран вы имеете, тем привлекательнее становиться ваша экономика и ваша валюта для других государств. \n\nВам необходимо заключать все больше экономических и дипломатических соглашений между разными участниками экономической системы и вне ее.'
                                               '</pre>',
                                               keyboard)
    except Exception as error:
        await callback_utils.handle_error(callback, error, 'Не удалось обновить сообщение при выходе раздела "эмиссия национальной валюты"')

