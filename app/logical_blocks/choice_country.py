from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

# Импортируйте модули, которые используются внутри функций
import app.DatabaseWork.master as master_db
import app.DatabaseWork.match as match_db
import app.keyboards.choice_country as kb
from app.message_designer.deletezer import delete_message_photo
from app.message_designer.randomaizer import generate_custom_random_unique_word
from app.utils import callback_utils

# Router setup
router = Router()

# import routers from logical_blocks
from app.logical_blocks.verify_country import router as verify_state_router
from app.logical_blocks.country_menu import router as country_menu_router

# connect routers from logical_blocks
router.include_router(verify_state_router)
router.include_router(country_menu_router)

from app.logical_blocks.country_menu import start_country_menu


CHOICE_MATCH_FOR_USER = 'ChoiceMatchForUser_'
CHOICE_COUNTRY_FROM_MATCH = 'ChoiceCountryFromMatch_'


@router.callback_query(lambda c: c.data and c.data.startswith(CHOICE_MATCH_FOR_USER))
async def start_choice_number_match_for_game_user(callback: CallbackQuery, state: FSMContext):
    """
    choice number match for game user

    :param callback: CallbackQuery
    :param state: FSMContext
    """
    try:
        number_match = callback_utils.parse_callback_data(callback.data, 'ChoiceMatchForUser')[0]
        await callback_utils.notify_user(callback, f"Вы выбрали матч с номером: {number_match}")
        await delete_message_photo(callback, state)

        request_country = await match_db.check_request_choice_country(number_match, callback.from_user.id)

        if request_country is False:
            data_country = await match_db.check_choice_country_in_match_db(number_match, callback.from_user.id)

            if data_country:
                await callback_utils.send_message(callback, f'<b>Вы играете за:</b> {data_country['name_country']}')
                await start_country_menu(callback)

            elif data_country is None:
                free_countries = await kb.free_countries_match(f'{CHOICE_COUNTRY_FROM_MATCH}{number_match}', number_match)

                if free_countries:
                    await callback_utils.send_message(callback,f'Выберите государство за которое играете, на карте: {number_match}.'
                                                  '<pre>Нужно указать только то государство, которым вы реально управляете в игре Supremacy1914.</pre>',
                                                      await kb.free_countries_match(f'{CHOICE_COUNTRY_FROM_MATCH}{number_match}', number_match))

                elif free_countries is None:
                    await callback_utils.send_message(callback,'К сожалению в данном матче свободных государств нет.')

                else:
                    await callback_utils.send_message(callback,'Что-то пошло не так "logical_blocks/choice_state/84"')

            else:
                await callback_utils.send_message(callback,'Что-то пошло не так "logical_blocks/choice_state/88"')

        elif request_country:
            await callback_utils.send_message(callback,'<b>Ваша заявка еще ожидает проверку.</b> '
                                          '\nСледуйте инструкции, которая была выпущена после выбора государства.')

        else:
            await callback_utils.send_message(callback, 'Что-то пошло не так "logical_blocks/choice_state/99"')
    except Exception as error:
        await callback_utils.handle_error(callback, error, "Не удалось обработать ваш выбор матча.")


@router.callback_query(lambda c: c.data and c.data.startswith(CHOICE_COUNTRY_FROM_MATCH))
async def choice_country_from_number_match_for_user(callback: CallbackQuery):
    """
    Пользователь выбирает государство для представления в матче.

    :param callback: CallbackQuery
    """
    try:
        data_parts = callback_utils.parse_callback_data(callback.data, 'ChoiceCountryFromMatch')
        number_match, name_country = data_parts[0], data_parts[1]

        await callback_utils.notify_user(callback, f"Вы выбрали государство: {name_country}")
        await callback_utils.send_edit_message(callback, 'Обработка...')

        unique_word = generate_custom_random_unique_word()

        instructions = (
            f"Следуйте этим инструкциям для подтверждения вашей заявки:\n"
            f"<pre>"
            f"1. Откройте Supremacy1914 и войдите в матч под номером: {number_match};\n"
            f"2. Найдите игрока 'Company Mekas' (он же 'International Monetary Fund');\n"
            f"3. Отправьте ему кодовое слово: {unique_word};\n"
            f"4. Ожидайте подтверждения вашей заявки.\n"
            f"</pre>\n"
            f"<pre>"
            f"Важно: не передавайте кодовое слово никому.\n"
            f"Это гарантирует вашу подлинность при выборе государства в матче.\n"
            f"</pre>"
        )

        await callback_utils.send_edit_message(callback, instructions)

        chat_id_admin = await master_db.get_telegram_id_admin()
        admin_message = (
            f"<b>Запрос на выбор государства</b>\n"
            f"<b>Матч:</b> {number_match}\n"
            f"<b>Государство:</b> {name_country}\n"
            f"<b>Кодовое слово:</b> {unique_word}"
        )

        admin_decision_message = await callback.bot.send_message(
            chat_id=chat_id_admin,
            text=admin_message,
            reply_markup=await kb.country_verify_by_admin(unique_word, number_match),
            parse_mode="html"
        )

        # save chat_id user and data request choice state
        await match_db.save_request_choice_country(callback.from_user.id, number_match, name_country, unique_word, admin_decision_message.message_id)

    except Exception as error:
        await callback_utils.handle_error(callback, error, "Не удалось обработать ваш выбор государства.")
