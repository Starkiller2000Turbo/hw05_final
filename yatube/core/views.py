from http import HTTPStatus

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls.exceptions import Resolver404


def page_not_found(
    request: HttpRequest,
    exception: Resolver404,
) -> HttpResponse:
    del exception
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    del reason
    return render(
        request,
        'core/403csrf.html',
        status=HTTPStatus.FORBIDDEN,
    )
