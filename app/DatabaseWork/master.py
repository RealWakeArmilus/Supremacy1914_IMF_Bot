import sqlite3

from SPyderSQL import SQLite, TypesSQLite


name_master_db = 'database/master.db'


async def created_table_match():
    SQLite.create_table(name_master_db,
                        'match',
                        {'number': TypesSQLite.integer.value, 'type_map' : TypesSQLite.text.value},
                        True)


async def created_match(number: int, type_map: str):
    """
    Created new match from table match

    :param number:
    :param type_map:
    :return:
    """
    await created_table_match()

    SQLite.insert_table(name_master_db,
                        'match',
                        ['number', 'type_map'],
                        (number, type_map))


async def check_number_match_exists(number: int) -> bool:
    """

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


