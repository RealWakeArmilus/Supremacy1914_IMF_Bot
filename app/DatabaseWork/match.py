import sqlite3
from SPyderSQL import SQLite


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
    data_number_match = SQLite.select_table(f'database/{number_match_db}.db',
                                            'countries',
                                            ['name', 'telegram_id'])

    countries_from_match = list()

    for data_country in data_number_match:
        if data_country['telegram_id'] == 0:
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
    data_requests = SQLite.select_table(f'database/{number_match_db}.db',
                                           'country_choice_requests',
                                           ['telegram_id'])

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
    data_country = SQLite.select_table(f'database/{number_match_db}.db',
                                           'countries',
                                           ['name', 'telegram_id'])

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
        assert isinstance(user_id, int), "user_id должен быть целым числом"
        assert isinstance(number_match, str) and number_match.isdigit(), "number_match должен быть числом в виде строки"
        assert isinstance(name_country, str), "name_country должен быть строкой"
        assert isinstance(unique_word, str), "unique_word должен быть строкой"
        assert isinstance(admin_decision_message_id, int), "admin_decision_message_id должен быть int"

        # Preparing data for insertion
        column_names = ['telegram_id', 'number_match', 'name_country', 'unique_word', 'admin_decision_message_id']
        values = (user_id, int(number_match), name_country, unique_word, admin_decision_message_id)

        # Checking data length
        if len(column_names) != len(values):
            raise ValueError(f"Mismatch between columns and values! Values: {values} for Columns: {column_names}")

        # Inserting data into the database
        SQLite.insert_table(f'database/{number_match}.db',
                            'country_choice_requests',
                            column_names,
                            values
        )
    except ValueError as error:
        print(f'Error "app/DatabaseWork/match/save_country_choice_requests": {error}')


async def get_data_country_choice_requests(unique_word: str, number_match: str) -> dict:
    """
    Возвращает все базовые данные заявки определённого матча, на регистрацию пользователя конкретного государства

    :param unique_word: кодовое слово
    :param number_match: номер матча
    :return: данные заявки {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match}
    """

    data_users = SQLite.select_table(f'database/{number_match}.db',
                                    'country_choice_requests',
                                    ['telegram_id', 'name_country', 'unique_word', 'admin_decision_message_id'])

    for user in data_users:
        if user['unique_word'] == unique_word:
            return {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match, 'unique_word': user['unique_word'], 'admin_decision_message_id': user['admin_decision_message_id']}


async def deleted_request_country_in_match(data_user: dict):
    """
    Удаляет заявку на подтверждения государства в конкретном матче

    :param data_user:
    """
    try:
        with sqlite3.connect(f'database/{data_user['number_match']}.db') as db:
            db.execute("DELETE FROM country_choice_requests WHERE unique_word = ?", (data_user['unique_word'],))
            db.commit()
            return True
    except sqlite3.Error as e:
        print(f"Ошибка при удалении заявки на подтверждения государства: {data_user['name_country']}: {e}")
        return False


async def register_country_in_match(data_user: dict):
    """
    Регистрирует пользователя в конкретном матче на конкретное государство. Совершать только после подтверждения админа.

    :param data_user: {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match}
    """
    # change telegram id of the appropriate country
    SQLite.update_table(f'database/{data_user['number_match']}.db',
                        'countries',
                        {'telegram_id': data_user['telegram_id']},
                        {'name': data_user['name_country']})

    await deleted_request_country_in_match(data_user)


async def get_data_country(user_id: int, number_match: str) -> dict | None:
    """
    Возвращает данные по государству

    :param user_id: message.from_user.id | callback.from_user.id
    :param number_match: number match
    :return: dict
    """
    try:
        data_countries = SQLite.select_table(f'database/{number_match}.db',
                                        'countries',
                                        ['id', 'telegram_id', 'name', 'admin'])
    except Exception as error:
        print(f"Ошибка при получении данных о странах: {error}. № Матч {number_match}.")
        return None

    characteristics_country : dict | None = None

    for data_country in data_countries:
        if data_country['telegram_id'] == user_id:
            characteristics_country = {
                'country_id': data_country['id'],
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
        data_currencies = SQLite.select_table(f'database/{number_match}.db',
                                            'currency',
                                            ['country_id', 'name', 'tick', 'emission', 'capitalization'])
    except Exception as error:
        print(f"Ошибка при получении данных о валюте: {error}. № Матч {number_match}.")
        return None

    currency_info : dict | False = False

    for data_currency in data_currencies:
        if data_currency['country_id'] == data_country['country_id']:
            currency_info = {
                'name': data_currency['name'],
                'tick': data_currency['tick'],
                'emission': data_currency['emission'],
                'capitalization': data_currency['capitalization']
            }
            break

    if not currency_info:
        # print(f"Данные о валюте не найдены для государства {data_country['name_country']}. № Матч {number_match}.")
        data_country['currency'].append(False)
    elif currency_info:
        data_country['currency'].append(currency_info)

    return data_country

