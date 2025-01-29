def format_number(number) -> str:
    """
    Форматирует большое число, разделяя разряды пробелами.

    :param number: Число для форматирования (int или float).
    :return: Строка с отформатированным числом.
    """
    if not isinstance(number, (int, float)):
        raise ValueError("Input must be an int or float.")

    # Разделяем целую и дробную части (если число float)
    integer_part, _, decimal_part = f"{number}".partition(".")
    formatted_integer = f"{int(integer_part):,}".replace(",", " ")
    return f"{formatted_integer}.{decimal_part}" if decimal_part else formatted_integer
