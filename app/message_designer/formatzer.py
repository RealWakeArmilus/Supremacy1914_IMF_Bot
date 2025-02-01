from decimal import Decimal


def format_number_ultra(number: float, course: bool = False):

    if course:
        number = round(Decimal(number), 6)
    if not course:
        number = f'{round(number, 2):,}'

    return str(number)

