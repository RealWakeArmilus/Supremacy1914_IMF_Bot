from SPyderSQL import AsyncSQLite

SPyderSQL = AsyncSQLite


async def extraction_names_countries(type_match: str) -> list:

    if type_match == 'Великая война':

        return ["Финляндия", "Австро-венгрия", "Аравия", "Великобритания", "Восточная ливия",
                "Восточный алжир", "Германская империя", "Гренландия", "Греция", "Египет",
                "Западная ливия", "Западный алжир", "Испания", "Италия", "Кавказ",
                "Литва", "Марокко", "Норвегия", "Османская империя", "Польша",
                "Россия", "Румыния", "Северная канада", "Северная россия", "Северные США",
                "Франция", "Центральные США", "Швеция", "Южная канада", "Южные США"]


async def get_free_countries_from_match_for_user(number_match_db: str) -> list:
    """
    :param number_match_db: 'database/{number_match_db}.db'
    :return: actual list free countries from match for user
    """
    SPyderSQLite = SPyderSQL(f'database/{number_match_db}.db')

    data_number_match = await SPyderSQLite.select(
        name_table='countries',
        names_columns=['name',
                       'telegram_id'
                       ]
    ).execute()

    countries_from_match = list()

    for data_country in data_number_match:
        if data_country['telegram_id'] is None:
            countries_from_match.append(data_country['name'])

    return countries_from_match


async def check_country_choice_requests(number_match_db: str, user_id: int) -> bool:
    """
    Is there a player's application in the database?
    \nЕсть ли заявка от игрока в базе данных?

    :param number_match_db: 'database/{number_match_db}.db'
    :param user_id: message.from_user.id
    :return: True - заявка еще ждет проверки, False - заявка нет.
    """
    SPyderSQLite = SPyderSQL(f'database/{number_match_db}.db')

    data_requests = await SPyderSQLite.select(
        name_table='country_choice_requests',
        names_columns=['telegram_id']
    ).execute()

    for request in data_requests:
        if request['telegram_id'] == user_id:
            return True

    return False


async def check_choice_country_in_match_db(number_match_db: str, user_id: int) -> dict | None:
    """
    checking the user in the list of countries. Perhaps his application has already been checked and approved.
    \nПроверка пользователя в списке государств. возможно его заявка уже прошла проверку и ее одобрили.
    \n\nIs the player already assigned to a specific country?
    \nИгрок уже закреплен за конкретным государством?

    :param number_match_db: 'database/{number_match_db}.db'
    :param user_id: message.from_user.id
    :return: dict - заявка прошла проверку и ее одобрили, None - заявка прошла проверку и ее отклонили.
    """
    SPyderSQLite = SPyderSQL(f'database/{number_match_db}.db')

    data_country = await SPyderSQLite.select(
        name_table='countries',
        names_columns=['name',
                       'telegram_id'
                       ]
    ).execute()

    for country in data_country:
        if country['telegram_id'] == user_id:
            return {'telegram_id': country['telegram_id'], 'name_country': country['name']}

    return None


async def save_country_choice_requests(user_id: int, number_match: str, name_country: str, unique_word: str, admin_decision_message_id: int):
    """
    Сохраняет заявку пользователя на выбор государства в базу данных.

    :param admin_decision_message_id:
    :param user_id: Telegram ID пользователя callback.from_user.id
    :param number_match: Номер матча
    :param name_country: Название выбранного государства
    :param unique_word: Кодовое слово
    """
    try:
        # Check for None
        if user_id is None or number_match is None or name_country is None or unique_word is None or admin_decision_message_id is None:
            raise ValueError("One or more parameters are missing! Missing required parameters.")

        # Checking Type Conformance
        if not isinstance(user_id, int):
            raise TypeError("user_id должен быть целым числом")
        if not (isinstance(number_match, str) and number_match.isdigit()):
            raise TypeError("number_match должен быть числом в виде строки")
        if not isinstance(name_country, str):
            raise TypeError("name_country должен быть строкой")
        if not isinstance(unique_word, str):
            raise TypeError("unique_word должен быть строкой")
        if not isinstance(admin_decision_message_id, int):
            raise TypeError("admin_decision_message_id должен быть int")

        # Preparing data for insertion
        column_names = ['telegram_id', 'number_match', 'name_country', 'unique_word', 'admin_decision_message_id']
        values = (user_id, int(number_match), name_country, unique_word, admin_decision_message_id)

        # Checking data length
        if len(column_names) != len(values):
            raise ValueError(f"Mismatch between columns and values! Values: {values} for Columns: {column_names}")

        # Inserting data into the database
        SPyderSQLite = SPyderSQL(f'database/{number_match}.db')

        await SPyderSQLite.insert(
            name_table='country_choice_requests',
            names_columns=column_names
        ).execute(parameters=values)
    except (ValueError, TypeError) as error:
        print(f'Error "app/DatabaseWork/match/save_country_choice_requests": {error}')


async def get_data_country_choice_request(unique_word: str, number_match: str) -> dict:
    """
    Возвращает все базовые данные заявки определённого матча, на регистрацию пользователя конкретного государства

    :param unique_word: кодовое слово
    :param number_match: номер матча
    :return: данные заявки {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match}
    """
    SPyderSQLite = SPyderSQL(f'database/{number_match}.db')

    data_users = await SPyderSQLite.select(
        name_table='country_choice_requests',
        names_columns=['telegram_id',
                       'name_country',
                       'unique_word',
                       'admin_decision_message_id'
                       ]
    ).execute()
    for user in data_users:
        if user['unique_word'] == unique_word:
            return {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match,
                    'unique_word': user['unique_word'], 'admin_decision_message_id': user['admin_decision_message_id']}


async def deleted_request_country_in_match(data_user: dict):
    """
    Удаляет заявку на подтверждения государства в конкретном матче

    :param data_user:
    """
    try:
        SPyderSQLite = SPyderSQL(f'database/{data_user['number_match']}.db')

        await SPyderSQLite.delete(
            name_table='country_choice_requests',
        ).where({'unique_word': data_user['unique_word']}).execute()
    except Exception as error:
        print(f"Ошибка при удалении заявки на подтверждения государства: {data_user['name_country']}: {error}")
        return False


async def register_country_in_match(data_user: dict):
    """
    Регистрирует пользователя в конкретном матче на конкретное государство. Совершать только после подтверждения админа.

    :param data_user: {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match}
    """
    # change telegram id of the appropriate country
    SPyderSQLite = SPyderSQL(f'database/{data_user['number_match']}.db')

    await SPyderSQLite.update(
        name_table='countries',
        data_set={'telegram_id': data_user['telegram_id']}
    ).where({'name': data_user['name_country']}).execute()

    await deleted_request_country_in_match(data_user)


async def get_data_country(user_id: int, number_match: str) -> dict | None:
    """
    Возвращает данные по государству

    :param user_id: message.from_user.id | callback.from_user.id
    :param number_match: number match
    :return: dict {country_id, name_country, status: {admin}, currency: [] }
    """
    try:
        SPyderSQLite = SPyderSQL(f'database/{number_match}.db')

        data_countries = await SPyderSQLite.select(
            name_table='countries',
            names_columns=['id',
                           'telegram_id',
                           'name',
                           'admin'
                           ]
        ).execute()
    except Exception as error:
        print(f"Ошибка при получении данных о странах: {error}. № Матч {number_match}.")
        return None

    characteristics_country : dict | None = None

    for data_country in data_countries:
        if data_country['telegram_id'] == user_id:
            characteristics_country = {
                'country_id': data_country['id'],
                'telegram_id': data_country['telegram_id'],
                'name_country': data_country['name'],
                'status': {'admin': data_country['admin']},
                'currency': []
            }
            break

    if not characteristics_country:
        print(f"Данные о стране не найдены для пользователя {user_id}. № Матч {number_match}.")
        return None

    return characteristics_country


async def get_data_currency(data_country: dict, number_match: str) -> dict | None:
    """
    Возвращает данные по валюте государства
    
    :param data_country: match_db.get_data_country()
    :param number_match: number match
    :return: 
    """
    try:
        columns = ['country_id',
                   'name',
                   'tick',
                   'following_resource',
                   'course_following',
                   'capitalization',
                   'emission',
                   'currency_index'
                   ]

        SPyderSQLite = SPyderSQL(f'database/{number_match}.db')

        data_currencies = await SPyderSQLite.select(
            name_table='currency',
            names_columns=columns
        ).execute()
    except Exception as error:
        print(f"Ошибка при получении данных о валюте: {error}. № Матч {number_match}.")
        return None

    currency_info : dict | False = False

    for data_currency in data_currencies:
        if data_currency['country_id'] == data_country['country_id']:
            currency_info = {
                'name': data_currency['name'],
                'tick': data_currency['tick'],
                'following_resource': data_currency['following_resource'],
                'course_following': data_currency['data_currency'],
                'capitalization': data_currency['capitalization'],
                'emission': data_currency['emission'],
                'currency_index': data_currency['currency_index']
            }
            break

    if not currency_info:
        # print(f"Данные о валюте не найдены для государства {data_country['name_country']}. № Матч {number_match}.")
        data_country['currency'].append(False)
    elif currency_info:
        data_country['currency'].append(currency_info)

    return data_country


async def check_name_currency_exists(number_match: str, name_currency: str):
    """
    Проверяет название валюты на существование в базе данных двойников

    :param number_match: number match
    :param name_currency: name currency
    :return:
    """
    SPyderSQLite = SPyderSQL(f'database/{number_match}.db')

    names_currency = await SPyderSQLite.select(
        name_table='currency',
        names_columns=['name']
    ).execute()

    for name in names_currency:
        if name['name'] == name_currency:
            return True

    return False


async def check_tick_currency_exists(number_match: str, tick_currency: str):
    """
    Проверяет название валюты на существование в базе данных двойников

    :param number_match: number match
    :param tick_currency: tick currency
    :return:
    """
    SPyderSQLite = SPyderSQL(f'database/{number_match}.db')

    ticks_currency = await SPyderSQLite.select(
        name_table='currency',
        names_columns=['tick']
    ).execute()

    for tick in ticks_currency:
        if tick['tick'] == tick_currency:
            return True

    return False


async def save_currency_emission_request(data_request: dict):
    """
    Сохраняет заявку государства на эмиссию валюты в базу данных.

    :param data_request: {'photo_message_id': 1787, 'number_match': '9480505', 'telegram_id': 5311154389, 'country_id': 4, 'name_currency': 'Черпак', 'tick_currency': 'HPK', 'amount_emission_currency': 5000000000, 'capitalization': 50000, 'date_request_creation': '2024-12-27 02:46:32', 'status_confirmed': False, 'date_confirmed': ''}
    """
    try:
        # Check for None
        required_fields = [
            'number_match',
            'data_country',
            'name_currency',
            'tick_currency',
            'following_resource',
            'course_following',
            'capitalization',
            'amount_emission_currency',
            'date_request_creation',
            'status_confirmed',
            'date_confirmed'
        ]

        if not all(field in data_request and data_request[field] is not None for field in required_fields):
            raise ValueError("One or more parameters are missing!")

        data_country = data_request['data_country']
        if not data_country:
            raise ValueError("'data_country' is missing in data_request.")

        # Checking Type Conformance
        if not (isinstance(data_request['number_match'], str) and data_request['number_match'].isdigit()):
            raise TypeError("number_match должен быть числом в виде строки.")
        if not isinstance(data_country['telegram_id'], int):
            raise TypeError("telegram_id должен быть int.")
        if not isinstance(data_country['country_id'], int):
            raise TypeError("country_id должен быть int.")
        if not isinstance(data_request['name_currency'], str):
            raise TypeError("name_currency должен быть строкой.")
        if not isinstance(data_request['tick_currency'], str):
            raise TypeError("tick_currency должен быть строкой.")
        if not isinstance(data_request['following_resource'], str):
            raise TypeError("following_resource должен быть строкой.")
        if not isinstance(data_request['course_following'], (float, int)):  # Позволяет int для гибкости
            raise TypeError("course_following должен быть float.")
        if not isinstance(data_request['capitalization'], int):
            raise TypeError("capitalization должен быть int.")
        if not isinstance(data_request['amount_emission_currency'], (float, int)):
            raise TypeError("amount_emission_currency должен быть float.")
        if not isinstance(data_request['date_request_creation'], str):
            raise TypeError("date_request_creation должен быть строкой.")
        if not isinstance(data_request['status_confirmed'], bool):
            raise TypeError("status_confirmed должен быть bool.")
        if not isinstance(data_request['date_confirmed'], str):
            raise TypeError("date_confirmed должен быть строкой.")


        # Preparing data for insertion
        column_names = [
            'number_match',
            'telegram_id',
            'country_id',
            'name_currency',
            'tick_currency',
            'following_resource',
            'course_following',
            'capitalization',
            'amount_emission_currency',
            'date_request_creation',
            'status_confirmed',
            'date_confirmed'
        ]

        values = (
            int(data_request['number_match']),
            data_request['data_country']['telegram_id'],
            data_request['data_country']['country_id'],
            data_request['name_currency'],
            data_request['tick_currency'],
            data_request['following_resource'],
            data_request['course_following'],
            data_request['capitalization'],
            data_request['amount_emission_currency'],
            data_request['date_request_creation'],
            data_request['status_confirmed'],
            data_request['date_confirmed']
        )

        # Checking data length
        if len(column_names) != len(values):
            raise ValueError(f"Mismatch between columns and values! Values: {values} for Columns: {column_names}")

        # Inserting data into the database
        SPyderSQLite = SPyderSQL(f'database/{int(data_request['number_match'])}.db')

        await SPyderSQLite.insert(
            name_table='currency_emission_requests',
            names_columns=column_names
        ).execute(parameters=values)
    except (ValueError, TypeError) as error:
        print(f'Error "app/DatabaseWork/match/save_currency_emission_requests": {error}')


async def get_data_form_emis_nat_currency_request(user_id: int, number_match: str):
    """
    Возвращает все базовые данные заявки эмиссии валюты, конкретного государства

    :param user_id: id пользователя
    :param number_match: номер матча
    :return: данные заявки {'id': request['id'],
                    'number_match': request['number_match'], 'telegram_id': request['telegram_id'], 'country_id': request['country_id'],
                    'name_currency': request['name_currency'], 'tick_currency': request['tick_currency'],
                    'following_resource': request['following_resource'], 'course_following': request['course_following'],
                    'capitalization': request['capitalization'], 'amount_emission_currency': request['amount_emission_currency'],
                    'date_request_creation': request['date_request_creation'],
                    'status_confirmed': request['status_confirmed'], 'date_confirmed': request['date_confirmed']}
    """
    SPyderSQLite = SPyderSQL(f'database/{number_match}.db')

    data_requests = await SPyderSQLite.select(
        name_table='currency_emission_requests',
        names_columns=['id',
                       'number_match',
                       'telegram_id',
                       'country_id',
                       'name_currency',
                       'tick_currency',
                       'following_resource',
                       'course_following',
                       'capitalization',
                       'amount_emission_currency',
                       'date_request_creation',
                       'status_confirmed',
                       'date_confirmed'
                       ]
    ).execute()

    for request in data_requests:
        if (request['telegram_id'] == user_id and
                not request['status_confirmed'] and
                request['date_confirmed'] == ''):
            return {
                'id': request['id'],
                'number_match': request['number_match'],
                'telegram_id': request['telegram_id'],
                'country_id': request['country_id'],
                'name_currency': request['name_currency'],
                'tick_currency': request['tick_currency'],
                'following_resource': request['following_resource'],
                'course_following': request['course_following'],
                'capitalization': request['capitalization'],
                'amount_emission_currency': request['amount_emission_currency'],
                'date_request_creation': request['date_request_creation'],
                'status_confirmed': request['status_confirmed'],
                'date_confirmed': request['date_confirmed']
            }
    return None

