from datetime import date


def calculate_age(birth_date: date) -> int:
    """
    Calcula la edad a partir de una fecha

    :param birth_date: Fecha de nacimiento
    :type birth_date: date
    :return: La edad en años
    :rtype: int
    """
    if not birth_date:
        return 0
    today = date.today()
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )
