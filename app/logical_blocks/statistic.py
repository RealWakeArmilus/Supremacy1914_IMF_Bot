from datetime import datetime
import pytz
import logging

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

import ClassesStatesMachine.SG as SG
from ClassesStatesMachine.SG import update_state
from app.DatabaseWork.database import DatabaseManager
from app.keyboards.universal import launch_solution
from app.message_designer.formatzer import format_number_ultra
from app.message_designer.deletezer import delete_message
from app.message_designer.chartzer import create_chart_currency_capitals_from_country
from app.utils import callback_utils


# Router setup
router = Router()


logger = logging.getLogger(__name__)


# Callback prefixes
PREFIXES = {
    "COUNTRIES": "Countries",
    "CURRENCIES": "Currencies"
}


@router.callback_query(lambda c: c.data and c.data.startswith(f'{PREFIXES["COUNTRIES"]}_'))
async def statistic_countries(callback: CallbackQuery):

    try:
        number_match = callback_utils.parse_callback_data(callback.data, PREFIXES["COUNTRIES"])[0]

        database_manager = DatabaseManager(database_path=number_match)

        busy_countries_data = await database_manager.get_template(
            name_table='countries',
            column_names=['id', 'name'],
            alone=False
        )

        if not busy_countries_data:
            raise Exception(f'busy_countries_data: {busy_countries_data}')

        timezone = pytz.timezone("Europe/Moscow")
        now_date = datetime.now(timezone).strftime("%Y-%m-%d")

        statistic_world_text = (
            "<b>Список государств пуст, невозможно сделать статистику.</b>"
            if not busy_countries_data else
            f"<b>Статистика государств и их валют на: <i>{now_date}.</i></b>\n"
        )

        count_country = 0

        for country_data in busy_countries_data:
            data_country = await database_manager.get_data_country(number_match=number_match, country_id=country_data['id'])
            data_currency = await database_manager.get_data_currency(data_country=data_country)

            if data_currency['telegram_id'] != 0:

                count_country += 1
                statistic_world_text += (
                    f"\n{count_country}. <b>{data_currency['name_country']}</b>\n"
                )

                if data_currency['currency'][0] is False:
                    statistic_world_text += (
                        "<blockquote>"
                        "    <i><b>Тг Ник:</b> </i>\n"
                        "</blockquote>"
                    )
                else:
                    statistic_world_text += (
                        "<blockquote>"
                        f"    <i><b>Тг Ник:</b> </i>\n"
                        f"    <i><b>Нац. валюта:</b> {data_currency['currency'][0]['name']} ({data_currency['currency'][0]['tick']})</i>\n"
                        f"    <i><b>Текущий курс:</b> {format_number_ultra(number=data_currency['currency'][0]['current_course'], course=True)} {data_currency['currency'][0]['following_resource']}</i>\n"
                        "</blockquote>"
                    )

        await callback_utils.send_edit_message(
            callback,
            text=statistic_world_text,
        )
    except Exception as error:
        await callback_utils.handle_exception(
            callback_or_message=callback,
            section='statistic_countries',
            error=error
        )


