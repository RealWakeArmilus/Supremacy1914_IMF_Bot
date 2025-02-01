from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import  Message, CallbackQuery

import ClassesStatesMachine.SG as SG
from ClassesStatesMachine.SG import update_state
from app.DatabaseWork.database import DatabaseManager
from app.keyboards.universal import verify_request_by_admin
from app.message_designer.deletezer import delete_message_photo, delete_message
from app.message_designer.randomaizer import generate_custom_random_unique_word
from app.utils import callback_utils


# Router setup
router = Router()

# import routers from logical_blocks
from app.logical_blocks.verify_country import router as verify_state_router
from app.logical_blocks.country_menu import router as country_menu_router
from app.logical_blocks.country_menu import start_country_menu

# connect routers from logical_blocks
router.include_router(verify_state_router)
router.include_router(country_menu_router)


CHOICE_MATCH_FOR_USER = 'ChoiceMatchForUser'
CHOICE_COUNTRY_FROM_MATCH = 'ChoiceCountryFromMatch'


@router.callback_query(lambda c: c.data and c.data.startswith(f'{CHOICE_MATCH_FOR_USER}_'))
async def start_choice_number_match_for_game_user(callback: CallbackQuery, state: FSMContext):
    """
    choice number match for game user

    :param callback: CallbackQuery
    :param state: FSMContext
    """
    try:
        number_match = callback_utils.parse_callback_data(callback.data, CHOICE_MATCH_FOR_USER)[0]
        await callback_utils.notify_user(callback, f"Вы выбрали матч с номером: {number_match}")
        await delete_message_photo(callback, state)

        request_country = await DatabaseManager(database_path=number_match).check_requests(name_requests='country_choice', user_id=callback.from_user.id)

        if request_country is False:
            data_country = await DatabaseManager(database_path=number_match).check_choice_country_in_match_db(user_id=callback.from_user.id)

            if data_country:
                await start_country_menu(callback=callback, number_match=number_match)

            elif data_country is None:

                free_countries_name = await DatabaseManager(database_path=number_match).get_countries_names(free=True)

                print(f'free_countries_name: {free_countries_name}')

                text = ''

                count_names = 0

                for country_name in free_countries_name:
                    count_names += 1
                    text += f'\n{count_names}. {country_name}'

                await state.set_state(SG.FormChoiceCountry.number_match)
                await update_state(state, number_match=number_match)

                await state.set_state(SG.FormChoiceCountry.message_id_delete)

                message_id = await callback_utils.send_message(callback,
                        text=f'<b>Выберите государство за которое играете, на карте:</b> {number_match}.'
                        '<pre>Нужно указать только то государство, которым вы реально управляете в игре Supremacy1914.</pre>\n'
                        f'{text}\n\n'
                        f'<b>Напишите выбранное название государства, точно как указано в списке. \nБЕЗ ПОРЯДКОВОГО НОМЕРА.</b>'
                )

                await update_state(state, message_id_delete=message_id)

            else:
                raise Exception('При обработке данных из списка государств произошла неизвестная ошибка')

        elif request_country:
            await callback_utils.send_message(callback,'<b>Ваша заявка еще ожидает проверку.</b> '
                                          '\nСледуйте инструкции, которая была выпущена после выбора государства.')
        else:
            raise Exception('При обработке заявок на регистрацию государства в матч произошла неизвестная ошибка')
    except Exception as error:
        await callback_utils.handle_error(callback, error, "Не удалось обработать вход в матч.")


@router.message(SG.FormChoiceCountry.message_id_delete)
async def end_country_from_number_match_for_user(message: Message, state: FSMContext):
    """
    Проверка названия государства, и вывод заявки в чат админа для решения на заявку.
    """
    try:
        input_search_name_country = message.text.strip()
        input_search_name_country = str(input_search_name_country).lower()

        form_choice_country = await state.get_data()
        number_match = form_choice_country['number_match']
        message_id_delete = form_choice_country['message_id_delete']

        names_country = await DatabaseManager(database_path=number_match).get_countries_names(free=True)

        if not names_country:
            raise ValueError("Не удалось получить список свободных государств, для сравнения с вашим введенным названием.")

        input_name_country: str = ''

        for name_country in names_country:
            if name_country.lower() == input_search_name_country:
                input_name_country = name_country

        if input_name_country == '':
            raise Exception(
                '\nВведенное названия не найдено в списке свободных государств.\n\n<b>Повторите свой ввод еще раз</b>')

        await delete_message(
            bot=message.bot,
            message_chat_id=message.chat.id,
            send_message_id=message_id_delete
        )



        processing_message = await message.answer('Обработка...')

        unique_word = generate_custom_random_unique_word()

        instructions = (
            f"<b>Вы выбрали государство:</b> {input_name_country}\n\n"
            f"<b>Следуйте этой инструкции, для подтверждения вашей заявки:</b>\n"
            f"<pre>"
            f"1. Откройте Supremacy1914 и войдите в матч под номером: {number_match};\n"
            f"2. Найдите игрока 'Company Mekas' (он же 'International Monetary Fund');\n"
            f"3. Отправьте ему кодовое слово;\n"
            f"4. Ожидайте подтверждения вашей заявки.\n"
            f"</pre>\n"
            f"<pre>"
            f"Важно: не передавайте кодовое слово никому.\n"
            f"Это гарантирует вашу подлинность при выборе государства в матче.\n"
            f"</pre>\n"
            "<b>Ваше кодовое слово</b>\n"
            f"<pre>"
            f"-----------------------------------------\n"
            f"Кодовое слово: {unique_word}\n\n"
            f"Название государства: {input_name_country}\n\n"
            f"Номер матча: {number_match}\n"
            f"-----------------------------------------"
            f"</pre>\n"
        )

        await processing_message.edit_text(
            text=instructions,
            parse_mode='html'
        )

        chat_id_admin = await DatabaseManager().get_owner_admin_telegram_id()

        admin_message = (
            f"<b>Запрос на выбор государства</b>\n"
            f"<b>Матч:</b> {number_match}\n"
            f"<b>Государство:</b> {input_name_country}\n"
            f"<b>Кодовое слово:</b> {unique_word}"
        )

        keyboard = await verify_request_by_admin(
            request_type='RequestCountryByAdmin',
            number_match=number_match,
            unique_word=unique_word
        )

        admin_decision_message = await message.bot.send_message(
            chat_id=chat_id_admin,
            text=admin_message,
            reply_markup=keyboard,
            parse_mode="html"
        )

        # save chat_id user and data request choice state
        await DatabaseManager(database_path=number_match).save_country_choice_requests(
            user_id=message.from_user.id,
            number_match=number_match,
            name_country=input_name_country,
            unique_word=unique_word,
            admin_decision_message_id=admin_decision_message.message_id
        )
    except (ValueError, Exception) as error:
        await callback_utils.handle_exception(message, 'end_country_from_number_match_for_user', error, '❌ <b>Ошибка на этапе выбора государства, для закрепления за ним.</b>')
