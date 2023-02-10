import typing
from datetime import datetime

from django.http import HttpRequest


def year(request: HttpRequest) -> typing.Dict[str, int]:
    """Добавляет переменную с текущим годом.

    Args:
        request: Передаваемый запрос.

    Returns:
        Текущий год в формате ГГГГ.
    """
    del request
    return {'year': datetime.now().date().year}
