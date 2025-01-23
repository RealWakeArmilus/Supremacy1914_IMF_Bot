import os
from datetime import datetime
import pytz

from asyncio.log import logger
from typing import List, Dict, Any, Optional

from SPyderSQL import AsyncSQLite

# Constants
MASTER_DB_PATH = 'database/master.db'


SPyderSQLite = AsyncSQLite


COUNTRIES_BY_TYPE_MATCH = {
    'Великая война': [
        "Финляндия", "Австро-венгрия", "Аравия", "Великобритания", "Восточная ливия",
        "Восточный алжир", "Германская империя", "Гренландия", "Греция", "Египет",
        "Западная ливия", "Западный алжир", "Испания", "Италия", "Кавказ",
        "Литва", "Марокко", "Норвегия", "Османская империя", "Польша",
        "Россия", "Румыния", "Северная канада", "Северная россия", "Северные США",
        "Франция", "Центральные США", "Швеция", "Южная канада", "Южные США"
    ],
    # Добавьте другие типы матчей по мере необходимости
}

def get_country_names(type_match: str) -> List[str]:
    return COUNTRIES_BY_TYPE_MATCH.get(type_match, [])




class DatabaseManager:

    count = 0  # Статическая переменная для хранения количества экземпляров

    def __init__(self, database_path: str = None):

        DatabaseManager.count += 1

        if database_path:
            self.SPyderSQLite = SPyderSQLite(f'database/{database_path}.db')
        else:
            self.SPyderSQLite = SPyderSQLite(MASTER_DB_PATH)


    def __del__(self):
        DatabaseManager.count -= 1

    def __repr__(self):
        return f"DatabaseManager('count:{self.count}', 'database_path:{self.SPyderSQLite}')"

    def __str__(self):
        return f"count:{self.count}', database_path:{self.SPyderSQLite}"


    async def create(self, table_name: str, columns: dict):
        """Создает таблицу в базе данных."""
        await self.SPyderSQLite.create(
            name_table=table_name,
            append_columns=columns,
            id_primary_key=True
        ).execute()

    async def insert(self, table_name: str, columns: List[str], values: tuple):
        """Вставляет запись в таблицу."""
        await self.SPyderSQLite.insert(
            name_table=table_name,
            names_columns=columns
        ).execute(parameters=values)

    async def select(self, table_name: str, columns: List[str] = None, where_clause: dict = None):
        """Выбирает записи из таблицы."""
        if columns and where_clause is None:
            return await self.SPyderSQLite.select(
                name_table=table_name,
                names_columns=columns,
            ).execute()

        elif where_clause and columns is None:
            return await self.SPyderSQLite.select(
                name_table=table_name
            ).where(conditions=where_clause).execute()

        elif None is (columns, where_clause):
            return await self.SPyderSQLite.select(
                name_table=table_name,
            ).execute()

        elif columns and where_clause:
            return await self.SPyderSQLite.select(
                name_table=table_name,
                names_columns=columns,
            ).where(conditions=where_clause).execute()

        else:
            logger.error('Что-то пошло не так. проблема в методе SELECT в DatabaseManager из app.DatabaseWork.database.py')
            return None

    async def delete(self, table_name: str, where_clause: dict):
        """Удаляет записи из таблицы."""
        await self.SPyderSQLite.delete(
            name_table=table_name,
        ).where(where_clause).execute()

    async def update(self, table_name: str, data_set: Dict[str, Any], where_clause: Dict[str, Any]):
        """Обновляет записи в таблице."""
        await self.SPyderSQLite.update(
            name_table=table_name,
            data_set=data_set
        ).where(where_clause).execute()


    async def set_admin(self, telegram_id: int):
        """Добавляет администратора в таблицу users из master.db."""
        await self.insert(
            table_name='users',
            columns=['telegram_id', 'admin'],
            values=(telegram_id, True)
        )

    async def get_admins_telegram_id(self) -> List[int] | None:
        """Возвращает список информации администрации из таблицы users из master.db"""
        data_admins = await self.select(
            table_name='users',
            where_clause={'admin': True}
        )
        return [data_admin['telegram_id'] for data_admin in data_admins]

    async def get_owner_admin_telegram_id(self) -> Optional[int] | None:
        """Возвращает telegram_id главного администратора."""
        admins_telegram_id = await self.get_admins_telegram_id()
        chat_id_admin = admins_telegram_id[0]

        return chat_id_admin


    async def match_exists(self, number_match: int) -> bool:
        """Проверяет существование матча по номеру."""
        result = await self.select(
            table_name='match',
            columns=['number'],
            where_clause={'number': number_match}
        )

        return bool(result)

    async def set_match(self, number_match: int, type_match: str):
        """Добавляет новый матч в master.db."""
        await self.insert(
            table_name='match',
            columns=['number', 'type_map'],
            values=(number_match, type_match)
        )

    async def get_all_match_numbers(self) -> List[int] | None:
        """Возвращает список всех номеров матчей."""
        matches = await self.select(
            table_name='match',
            columns=['number']
        )
        return [match['number'] for match in matches]


    async def set_country_names(self, type_match):
        """Добавляет список стран в таблицу countries"""
        country_names = get_country_names(type_match)
        for name_country in country_names:
            await self.insert(
                table_name='countries',
                columns=['name', 'admin'],
                values=(name_country, False)
            )

    async def get_free_country_names(self):
        """Возвращает список свободных стран из таблицы countries"""
        data_number_match = await self.select(
            table_name='countries',
            columns=['name', 'telegram_id']
        )
        countries_from_match = list()
        for data_country in data_number_match:
            if data_country['telegram_id'] is None:
                countries_from_match.append(data_country['name'])

        return countries_from_match


    async def initialize_master(self):
        """Инициализирует базу данных master.db и таблицы в ней [users, match]"""
        tables = {
            'users': {
                'telegram_id': 'INTEGER',
                'admin': 'BLOB'
            },
            'match': {
                'number': 'INTEGER',
                'type_map': 'TEXT'
            }
        }

        for table_name, columns in tables.items():
            await self.create(
                table_name=table_name,
                columns=columns
            )

        await self.set_admin(5311154389)

    async def initialize_match(self, type_match: str):
        """
        Инициализирует новый матч.

        :param type_match: Тип карты матча.
        :var set_match(number_match, type_match): Добавляет новый матч в таблицу match в master.db.
        """
        tables = {
            'countries': {
                'name': 'TEXT',
                'telegram_id': 'INTEGER',
                'admin': 'BLOB'
            },
            'country_choice_requests': {
                'telegram_id': 'INTEGER',
                'number_match': 'INTEGER',
                'name_country': 'TEXT',
                'unique_word': 'TEXT',
                'admin_decision_message_id': 'INTEGER'
            },
            'currency': {
                'country_id': 'INTEGER',
                'name': 'TEXT',
                'tick': 'TEXT',
                'following_resource': 'TEXT',
                'course_following': 'REAL',
                'capitalization': 'INTEGER',
                'emission': 'REAL',
                'current_amount': 'REAL',
                'current_course': 'REAL'
            },
            'currency_emission_requests': {
                'number_match': 'INTEGER',
                'telegram_id': 'INTEGER',
                'country_id': 'INTEGER',
                'name_currency': 'TEXT',
                'tick_currency': 'TEXT',
                'following_resource': 'TEXT',
                'course_following': 'REAL',
                'capitalization': 'INTEGER',
                'amount_emission_currency': 'REAL',
                'date_request_creation': 'TEXT',
                'status_confirmed': 'BLOB',
                'date_confirmed': 'TEXT',
                'message_id_delete': 'INTEGER'
            }
        }

        for table_name, columns in tables.items():
            await self.create(
                table_name=table_name,
                columns=columns
            )

        # Добавление стран
        await self.set_country_names(type_match=type_match)

    async def initialize_currency_capitals_for_country(self, user_id: int, number_match: str):
        """
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param user_id: message. from_user. id | callback. from_user. id
        :param number_match: – number match
        """
        data_country = await self.get_data_country(
            user_id=user_id,
            number_match=number_match
        )
        data_currency = await self.get_data_currency(
            data_country=data_country,
            number_match=number_match
        )

        tables = {
            f'currency_capitals_{data_country['country_id']}': {
                'currency_id': 'INTEGER',
                'amount': 'REAL'
            }
        }

        for table_name, columns in tables.items():
            await self.create(
                table_name=table_name,
                columns=columns
            )

        await self.set_capital_national_currency(data_currency=data_currency['currency'][0])


    async def delete_match_record(self, number_match: str) -> bool:
        """Удаляет запись матча из мастер-базы."""
        try:
            number = int(number_match)
            await self.delete(
                table_name='match',
                where_clause={'number': number}
            )
            return True
        except ValueError:
            print(f"Неверный формат номера матча: {number_match}")
            return False
        except Exception as e:
            print(f"Ошибка при удалении матча {number_match}: {e}")
            return False

    async def delete_match(self, number_match: str) -> bool:
        """Удаляет матч из мастер-базы и саму соответствующую базу данных."""
        database_path = f'database/{number_match}.db'

        try:
            if os.path.exists(database_path):

                os.remove(database_path)
                print(f"База данных {database_path} успешно удалена.")

                success = await self.delete_match_record(number_match)

                if not success:

                    return False
            else:
                raise Exception(f"Файл {database_path} не найден.")

            return True
        except Exception as error:
            print(f"Ошибка при удалении номера матча {number_match} из таблицы match: {error}")
            return False


    async def check_requests(self, name_requests: str, user_id: int) -> bool | None:
        """
        \nПроверка на существование заявки в таблицах
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param name_requests: country_choice - заявка на резервацию государства, currency_emission - заявка на эмиссию валюты
        :param user_id: message.from_user.id
        :return: True - есть заявка, False - нет заявка, None - если не правильный name_requests
        """

        try:
            if name_requests == 'country_choice':
                column_names = ['telegram_id']
                name_requests = 'country_choice_requests'
            elif name_requests == 'currency_emission':
                column_names = ['telegram_id', 'status_confirmed', 'date_confirmed']
                name_requests = 'currency_emission_requests'
            else:
                raise Exception('Не правильно выбрано название таблицы заявок, для проверки заявки.')

            data_requests = await self.select(
                table_name=name_requests,
                columns=column_names
            )

            if name_requests == 'country_choice_requests':
                for request in data_requests:
                    if request['telegram_id'] == user_id:
                        return True
            elif name_requests == 'currency_emission_requests':
                for request in data_requests:
                    if request['telegram_id'] == user_id and request['status_confirmed'] == 0 and request['date_confirmed'] == '':
                        return True

            return False
        except Exception as error:
            print(f'ERROR: {error}')
            return None

    async def check_choice_country_in_match_db(self, user_id: int) -> dict | None:
        """
        checking the user in the list of countries. Perhaps his application has already been checked and approved.
        \nПроверка пользователя в списке государств. возможно его заявка уже прошла проверку и ее одобрили.
        \n\nIs the player already assigned to a specific country?
        \nИгрок уже закреплен за конкретным государством?
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param user_id: message.from_user.id
        :return: dict - заявка прошла проверку и ее одобрили, None - заявка прошла проверку и ее отклонили.
        """
        column_names = ['name', 'telegram_id']

        data_country = await self.select(
            table_name='countries',
            columns=column_names
        )

        for country in data_country:
            if country['telegram_id'] == user_id:
                return {'telegram_id': country['telegram_id'], 'name_country': country['name']}

        return None

    async def save_country_choice_requests(self, user_id: int, number_match: str, name_country: str, unique_word: str, admin_decision_message_id: int):
        """
        Сохраняет заявку пользователя на выбор государства в базу данных.
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

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

            await self.insert(
                table_name='country_choice_requests',
                columns=column_names,
                values=values
            )
        except (ValueError, TypeError) as error:
            print(f'Ошибка при сохранении заявки на выбор государства, при регистрации на матч: {error}')

    async def get_data_country_choice_request(self, unique_word: str, number_match: str) -> dict:
        """
        Возвращает все базовые данные заявки определённого матча, на регистрацию пользователя конкретного государства
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param unique_word: кодовое слово
        :param number_match: номер матча
        :return: данные заявки {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match}
        """
        column_names = ['telegram_id', 'name_country', 'unique_word', 'admin_decision_message_id']

        data_users = await self.select(
            table_name='country_choice_requests',
            columns=column_names
        )

        for user in data_users:
            if user['unique_word'] == unique_word:
                return {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match,
                        'unique_word': user['unique_word'], 'admin_decision_message_id': user['admin_decision_message_id']}

    async def deleted_request_country_in_match(self, data_user: dict):
        """
        Удаляет заявку на подтверждения государства в конкретном матче
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param data_user:
        """
        try:
            where_clause = {'unique_word': data_user['unique_word']}

            await self.delete(
                table_name='country_choice_requests',
                where_clause=where_clause
            )

        except Exception as error:
            print(f"Ошибка при удалении заявки на подтверждения государства: {data_user['name_country']}: {error}")
            return False

    async def register_country_in_match(self, data_user: dict):
        """
        Регистрирует пользователя в конкретном матче на конкретное государство. Совершать только после подтверждения админа.
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param data_user: {'telegram_id': user['telegram_id'], 'name_country': user['name_country'], 'number_match': number_match}
        """
        # change telegram id of the appropriate country
        data_set = {'telegram_id': data_user['telegram_id']}
        where_clause = {'name': data_user['name_country']}

        await self.update(
            table_name='countries',
            data_set=data_set,
            where_clause=where_clause
        )

        await self.deleted_request_country_in_match(data_user)


    async def get_data_country(self, user_id: int, number_match: str) -> dict | None:
        """
        Возвращает данные по государству
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param user_id: message.from_user.id | callback.from_user.id
        :param number_match: number match
        :return: dict {country_id, name_country, status: {admin}, currency: [] }
        """
        try:
            column_names = ['id', 'telegram_id', 'name', 'admin']

            data_countries = await self.select(
                table_name='countries',
                columns=column_names
            )

        except Exception as error:
            print(f"Ошибка при получении данных о странах: {error}. № Матч {number_match}.")
            return None

        characteristics_country: dict | None = None

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

    async def get_data_currency(self, data_country: dict, number_match: str) -> dict | None:
        """
        Возвращает данные по валюте государства
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)


        :param data_country: match_db.get_data_country()
        :param number_match: number match
        :return: {'id','country_id','name','tick','following_resource','course_following','capitalization','emission','current_amount','current_course'}
        """
        try:
            column_names = [
                'id',
                'country_id',
                'name',
                'tick',
                'following_resource',
                'course_following',
                'capitalization',
                'emission',
                'current_amount',
                'current_course'
            ]

            data_currencies = await self.select(
                table_name='currency',
                columns=column_names
            )

        except Exception as error:
            print(f"Ошибка при получении данных о валюте: {error}. № Матч {number_match}.")
            return None

        currency_info: dict | False = False

        for data_currency in data_currencies:
            if data_currency['country_id'] == data_country['country_id']:
                currency_info = {
                    'id': data_currency['id'],
                    'country_id': data_currency['country_id'],
                    'name': data_currency['name'],
                    'tick': data_currency['tick'],
                    'following_resource': data_currency['following_resource'],
                    'course_following': data_currency['course_following'],
                    'capitalization': data_currency['capitalization'],
                    'emission': data_currency['emission'],
                    'current_amount': data_currency['current_amount'],
                    'current_course': data_currency['current_course']
                }
                break

        if not currency_info:
            # print(f"Данные о валюте не найдены для государства {data_country['name_country']}. № Матч {number_match}.")
            data_country['currency'].append(False)
        elif currency_info:
            data_country['currency'].append(currency_info)

        return data_country

    async def get_data_form_emis_nat_currency_request(self, user_id: int):
        """
        Возвращает все базовые данные заявки эмиссии валюты, конкретного государства

        :param user_id: id пользователя
        :return: данные заявки {'id': request['id'],
                        'number_match': request['number_match'], 'telegram_id': request['telegram_id'], 'country_id': request['country_id'],
                        'name_currency': request['name_currency'], 'tick_currency': request['tick_currency'],
                        'following_resource': request['following_resource'], 'course_following': request['course_following'],
                        'capitalization': request['capitalization'], 'amount_emission_currency': request['amount_emission_currency'],
                        'date_request_creation': request['date_request_creation'],
                        'status_confirmed': request['status_confirmed'], 'date_confirmed': request['date_confirmed']}
        """
        column_names = [
            'id',
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
            'date_confirmed',
            'message_id_delete'
        ]

        data_requests = await self.select(
            table_name='currency_emission_requests',
            columns=column_names,
        )

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
                    'date_confirmed': request['date_confirmed'],
                    'message_id_delete': request['message_id_delete']
                }
        return None

        # TODO придумать нужно где идет поиск одной заявки, а не всех. чтобы вывести ее, а не перебирать список заявок.

        # where = {'telegram_id': user_id, 'status_confirmed': False, 'date_confirmed': ''}
        #
        # request = await self.select(
        #     table_name='currency_emission_requests',
        #     columns=column_names,
        #     where_clause=where
        # )
        #
        # if request:
        #     return {
        #             'id': request['id'],
        #             'number_match': request['number_match'],
        #             'telegram_id': request['telegram_id'],
        #             'country_id': request['country_id'],
        #             'name_currency': request['name_currency'],
        #             'tick_currency': request['tick_currency'],
        #             'following_resource': request['following_resource'],
        #             'course_following': request['course_following'],
        #             'capitalization': request['capitalization'],
        #             'amount_emission_currency': request['amount_emission_currency'],
        #             'date_request_creation': request['date_request_creation'],
        #             'status_confirmed': request['status_confirmed'],
        #             'date_confirmed': request['date_confirmed'],
        #             'message_id_delete': request['message_id_delete']
        #         }
        # return None


    async def check_data_currency_exists(self, name_currency: str = '', tick_currency: str = '') -> bool | None:
        """
        Проверка данных валюты, на совпадение в базе данных.
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param name_currency: Название валюты
        :param tick_currency: Тикер валюты
        :return: True - есть совпадение, False - нет совпадений, None - ничего не проверяется
        """
        column_names = []
        name_parameter : str = ''
        check_parameter = None

        try:
            if name_currency != '':
                column_names = ['name']
                name_parameter = 'name'
                check_parameter = name_currency
            elif tick_currency != '':
                column_names = ['tick']
                name_parameter = 'tick'
                check_parameter = tick_currency
            elif name_currency == '' or tick_currency == '':
                raise Exception('При проверке данных валюты, на совпадение, ничего не было введено для проверки')

            parameters_currency = await self.select(
                table_name='currency',
                columns=column_names
            )

            for parameter in parameters_currency:
                if parameter[name_parameter] == check_parameter:
                    return True

            return False
        except Exception as error:
            print(f'Error: {error}')
            return None

    async def save_currency_emission_request(self, data_request: dict, message_id_delete: int):
        """
        Сохраняет заявку государства на эмиссию валюты в базу данных.
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param message_id_delete: сообщение которое нужно удалить в чате администратора
        :param data_request: {'number_match': '9480505', 'telegram_id': 5311154389,
        'country_id': 4, 'name_currency': 'Черпак', 'tick_currency': 'HPK', 'amount_emission_currency': 5000000000,
        'capitalization': 50000, 'date_request_creation': '2024-12-27 02:46:32', 'status_confirmed': False, 'date_confirmed': '', 'message_id_delete': 1787}
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
                'date_confirmed',
                'message_id_delete'
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
            if not isinstance(message_id_delete, int):
                raise TypeError("message_id_delete должен быть int.")

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
                'date_confirmed',
                'message_id_delete'
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
                data_request['date_confirmed'],
                message_id_delete
            )

            # Checking data length
            if len(column_names) != len(values):
                raise ValueError(f"Mismatch between columns and values! Values: {values} for Columns: {column_names}")

            # Inserting data into the database
            await self.insert(
                table_name='currency_emission_requests',
                columns=column_names,
                values=values
            )
        except (ValueError, TypeError) as error:
            print(f'Error "DatabaseManager/save_currency_emission_request": {error}')

    async def register_currency_emission_in_match(self, data_request: dict, result_verify: bool = True):
        """
        Регистрирует эмиссию национальной валюты в конкретном матче на конкретное государство. Совершать только после подтверждения админа.
        \n\nОбязательно поставьте номер матча, в DatabaseManager(database_path=number_match)

        :param result_verify: решение администратора по заявке
        :param data_request: данные заявки {'id': request['id'],
                    'number_match': request['number_match'], 'telegram_id': request['telegram_id'], 'country_id': request['country_id'],
                    'name_currency': request['name_currency'], 'tick_currency': request['tick_currency'],
                    'following_resource': request['following_resource'], 'course_following': request['course_following'],
                    'capitalization': request['capitalization'], 'amount_emission_currency': request['amount_emission_currency'],
                    'date_request_creation': request['date_request_creation'],
                    'status_confirmed': request['status_confirmed'], 'date_confirmed': request['date_confirmed']}
        """
        timezone = pytz.timezone("Europe/Moscow")
        now_date = datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")

        data_set = {'status_confirmed': result_verify, 'date_confirmed': now_date}
        where_clause = {'id': data_request['id']}

        await self.update(
            table_name='currency_emission_requests',
            data_set=data_set,
            where_clause=where_clause
        )

        if result_verify:
            column_names = [
                'country_id',
                'name',
                'tick',
                'following_resource',
                'course_following',
                'capitalization',
                'emission',
                'current_amount',
                'current_course'
            ]

            current_course = (data_request['amount_emission_currency'] / data_request['amount_emission_currency'])
            current_course = current_course * data_request['course_following']
            current_course = 1 / current_course
            current_course = round(current_course, 9)

            values = (
                data_request['country_id'],
                data_request['name_currency'],
                data_request['tick_currency'],
                data_request['following_resource'],
                data_request['course_following'],
                data_request['capitalization'],
                data_request['amount_emission_currency'],
                data_request['amount_emission_currency'],
                current_course
            )

            await self.insert(
                table_name='currency',
                columns=column_names,
                values=values
            )


    async def set_capital_national_currency(self, data_currency: dict):
        """
        установка национальной валюты в таблицу капиталов валют, конкретного государства.
        """
        print(f'data_currency: {data_currency}')

        country_id = data_currency['country_id']
        currency_id = data_currency['id']
        amount = data_currency['current_amount']

        table_name = f'currency_capitals_{country_id}'
        column_names = ['currency_id', 'amount']
        values = (currency_id, amount)

        await self.insert(
            table_name=table_name,
            columns=column_names,
            values=values
        )
