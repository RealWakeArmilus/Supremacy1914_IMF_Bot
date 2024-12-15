from SPyderSQL import SQLite, TypesSQLite


name_master_db = 'database/master.db'


def created_table_match():
    SQLite.create_table(name_master_db,
                        'match',
                        {'number': TypesSQLite.integer.value, 'type_map' : TypesSQLite.text.value},
                        True)


def created_match(number: int, type_map: str):
    """
    Created new match from table match

    :param number:
    :param type_map:
    :return:
    """
    created_table_match()

    SQLite.insert_table(name_master_db,
                        'match',
                        ['number', 'type_map'],
                        (number, type_map))


def check_number_match_exists(number: int) -> bool:
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



