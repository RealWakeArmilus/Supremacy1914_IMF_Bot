def format_large_number(number):
    """
    Форматирует большое число, разделяя разряды пробелами.

    :param number: Число для форматирования (int или float).
    :return: Строка с отформатированным числом.
    """
    if not isinstance(number, (int, float)):
        raise ValueError("Input must be an integer or float.")

    # Разделяем целую и дробную части (если число float)
    if isinstance(number, float):
        integer_part, decimal_part = str(number).split('.')
        formatted_integer = f"{int(integer_part):,}".replace(",", " ")
        return f"{formatted_integer}.{decimal_part}"
    else:
        # Для целых чисел
        return f"{number:,}".replace(",", " ")