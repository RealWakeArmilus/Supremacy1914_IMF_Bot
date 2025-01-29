
async def hash_callback_suffix_64_name_state(input_match_hash: str, callback_data: str, name_state: str) -> str:
    """
    :param input_match_hash: тот запрос, который отслеживает callback при нажатии кнопки.
    :param callback_data: Тот запрос, который отслеживает callback при нажатии кнопки f"{input_match_hash}_{name_state}"
    :param name_state: название государства
    :return: сокращает длинное слово на хэш не более 64 бита
    """
    if len(callback_data.encode('utf-8')) > 64:
        # Обработка слишком длинных callback_data
        # Например, использование хеширования или сокращение имени
        import hashlib

        hash_suffix = hashlib.md5(name_state.encode()).hexdigest()[:10]
        return f"{input_match_hash}_{hash_suffix}"
    else:
        return callback_data
