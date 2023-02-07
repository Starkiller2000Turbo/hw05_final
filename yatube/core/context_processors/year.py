from datetime import datetime

from django.http import HttpRequest


def year(request: HttpRequest) -> dict:
    """Добавляет переменную с текущим годом.

    Args:
        request: Передаваемый запрос.

    Returns:
        Возвращает текущий год в формате ГГГГ.
    """
    del request
    return {'year': datetime.now().date().year}
