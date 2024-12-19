from SPyderSQL import SQLite

async def extraction_names_states(type_map_match: str) -> list:

    if type_map_match == 'Великая война':

        return ["Финляндия", "Австро-венгрия", "Аравия", "Великобритания", "Восточная ливия",
                "Восточный алжир", "Германская империя", "Гренландия", "Греция", "Египет",
                "Западная ливия", "Западный алжир", "Испания", "Италия", "Кавказ",
                "Литва", "Марокко", "Норвегия", "Османская империя", "Польша",
                "Россия", "Румыния", "Северная канада", "Северная россия", "Северные США",
                "Франция", "Центральные США", "Швеция", "Южная канада", "Южные США"]


async def get_free_states_from_match_for_user(number_match_db: str) -> list:
    """
    :param number_match_db: 'database/{number_match_db}.db'
    :return: actual list free states from match for user
    """
    data_number_match = SQLite.select_table(f'database/{number_match_db}.db',
                                            'states',
                                            ['name', 'telegram_id'])

    states_from_match = list()

    for data_state in data_number_match:
        if data_state['telegram_id'] == 0:
            states_from_match.append(data_state['name'])

    return states_from_match
