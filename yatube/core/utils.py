from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(request: HttpRequest, queryset: QuerySet, on_page: int) -> Page:
    paginator = Paginator(queryset, on_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
