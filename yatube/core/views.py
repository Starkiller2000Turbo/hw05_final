from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls.exceptions import Resolver404


def page_not_found(
    request: HttpRequest,
    exception: Resolver404,
) -> HttpResponse:
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponse:
    return render(request, 'core/403csrf.html')
