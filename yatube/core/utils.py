from django.conf import settings
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    queryset: QuerySet,
    on_page: int = settings.OBJECTS_ON_PAGE,
) -> Page:
    return Paginator(queryset, on_page).get_page(request.GET.get('page'))
