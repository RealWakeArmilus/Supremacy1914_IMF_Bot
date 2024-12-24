import os
import sqlite3

from SPyderSQL import SQLite, TypesSQLite
import app.DatabaseWork.match as match_db


name_master_db = 'database/master.db'


async def created_match(number_match: int, type_match: str):
    """
    creates all the necessary environment for the match
    /nСоздает всю необходимую среду для матча

    :param number_match: number match
    :param type_match: type map match
    """
    SQLite.create_table(name_master_db,
                        'match',
                        {'number': TypesSQLite.integer.value, 'type_map' : TypesSQLite.text.value},
                        True)

    SQLite.insert_table(name_master_db,
                        'match',
                        ['number', 'type'],
                        (number_match, type_match))

    SQLite.create_table(f'database/{number_match}.db',
                        'countries',
                        {'name': TypesSQLite.text.value, 'telegram_id': TypesSQLite.integer.value, 'admin': TypesSQLite.blob.value},
                        True)

    SQLite.create_table(f'database/{number_match}.db',
                        'country_choice_requests',
                        {'telegram_id': TypesSQLite.integer.value, 'number_match': TypesSQLite.integer.value, 'name_country': TypesSQLite.text.value, 'unique_word': TypesSQLite.text.value, 'admin_decision_message_id': TypesSQLite.integer.value},
                        True)

    data_name_countries = await match_db.extraction_names_countries(type_match)

    for name_country in data_name_countries:
        SQLite.insert_table(f'database/{number_match}.db',
                            'countries',
                            ['name', "admin"],
                            (name_country, False))

    SQLite.create_table(f'database/{number_match}.db',
                        'currency',
                        {'country_id': TypesSQLite.integer.value, 'name': TypesSQLite.text.value, 'tick': TypesSQLite.text.value, 'emission': TypesSQLite.integer.value, 'capitalization': TypesSQLite.integer.value},
                        True)

    SQLite.create_table(f'database/{number_match}.db',
                        'currency_emission_requests',
                        {'telegram_id': TypesSQLite.integer.value, 'number_match': TypesSQLite.integer.value, 'name_country': TypesSQLite.text.value, 'unique_word': TypesSQLite.text.value, 'admin_decision_message_id': TypesSQLite.integer.value},
                        True)


async def check_number_match_exists(number: int) -> bool:
    """
    Проверяет номер матча на существование в базе данных

    :param number: number_match
    :return:
    """
    SQLite.create_table(name_master_db,
                        'match',
                        {'number': TypesSQLite.integer.value, 'type': TypesSQLite.text.value},
                        True)

    number_matches = SQLite.select_table(name_master_db,
                                         'match',
                                         ['number'])

    for number_match in number_matches:

        if number_match['number'] == number:

            return True

    return False


async def get_numbers_match() -> list:
    """
    :return: actual list numbers match in bot database master table match
    """
    data_number_match = SQLite.select_table(name_master_db,
                              'match',
                              ['number'])

    numbers_match = list()

    for number_match in data_number_match:
        numbers_match.append(number_match['number'])

    return numbers_match


async def deleted_match(number_match: str):
    """
    Асинхронно удаляет номер карты из таблицы `match` базы данных `master.db`.

    :param number_match: Номер карты для удаления.
    :return: True, если удаление прошло успешно, иначе False.
    """
    try:
        with sqlite3.connect(name_master_db) as db:
            db.execute("DELETE FROM match WHERE number = ?", (number_match,))
            db.commit()

        database_path = f'database/{number_match}.db'

        # Проверка, существует ли файл
        if os.path.exists(database_path):
            os.remove(database_path)
            print(f"База данных {database_path} успешно удалена.")
        else:
            raise Exception(f"Файл {database_path} не найден.")

        return True
    except (sqlite3.Error, Exception) as e:
        print(f"Ошибка при удалении номера матча {number_match} из таблицы match: {e}")
        return False


async def created_table_user():
    """
    Создает с нуля базу данных master и таблицу users
    """
    SQLite.create_table(name_master_db,
                        'users',
                        {'telegram_id': TypesSQLite.integer.value, 'admin': TypesSQLite.integer.value},
                        True)


async def set_telegram_id_admin():
    """
    Загружает в базу данных master и таблицу users данные главного админа бота
    """
    SQLite.insert_table(name_master_db,
                        'users',
                        ['telegram_id', 'admin'],
                        (5311154389, True))


async def get_telegram_id_admin() -> int:
    """
    :return: telegram_id admin bota
    """
    data_users = SQLite.select_table(name_master_db,
                                     'users',
                                     ['telegram_id', 'admin'])

    for user in data_users:
        if user['admin']:
            return user['telegram_id']




