import sqlite3

from SPyderSQL import SQLite, TypesSQLite
from app.DatabaseWork.match import extraction_names_states


name_master_db = 'database/master.db'


async def created_match(number_match: int, type_map: str):
    """
    Created new match from table match

    :param number_match: number match
    :param type_map: type map match
    :return:
    """
    SQLite.create_table(name_master_db,
                        'match',
                        {'number': TypesSQLite.integer.value, 'type_map' : TypesSQLite.text.value},
                        True)

    SQLite.insert_table(name_master_db,
                        'match',
                        ['number', 'type_map'],
                        (number_match, type_map))

    SQLite.create_table(f'database/{number_match}.db',
                        'states',
                        {'name': TypesSQLite.text.value, 'telegram_id': TypesSQLite.integer.value, 'admin': TypesSQLite.blob.value},
                        True)

    data_name_states = await extraction_names_states(type_map)

    for name_state in data_name_states:
        SQLite.insert_table(f'database/{number_match}.db',
                            'states',
                            ['name', "admin"],
                            (name_state, False))


async def check_number_match_exists(number: int) -> bool:
    """
    Проверяет номер матча на существование в базе данных

    :param number: number_map
    :return:
    """
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
            return True
    except sqlite3.Error as e:
        print(f"Ошибка при удалении номера карты {number_match}: {e}")
        return False


async def check_choice_state_in_match_db(number_match_db: str, user_id: int) -> bool:
    """
    Проверка пользователя на выбор государства в конкретном матче

    :param number_match_db: 'database/{number_match_db}.db'
    :param user_id: message.from_user.id
    :return: True - пользователь уже выбрал государство, False - пользователь не выбирал государства
    """
    data_telegram_id = SQLite.select_table(f'database/{number_match_db}.db',
                                           'states',
                                           ['telegram_id'])

    for telegram_id in data_telegram_id:
        if telegram_id == user_id:
            return True

    return False


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
