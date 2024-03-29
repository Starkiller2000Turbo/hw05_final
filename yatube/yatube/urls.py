from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


handler404 = 'core.views.page_not_found'
handler403 = 'core.views.csrf_failure'

urlpatterns = [
    path(
        'about/',
        include('about.urls', namespace=apps.get_app_config('about').name),
    ),
    path('admin/', admin.site.urls),
    path(
        'auth/',
        include('users.urls', namespace=apps.get_app_config('users').name),
    ),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        '',
        include('posts.urls', namespace=apps.get_app_config('posts').name),
    ),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)

if settings.DEBUG:
    import debug_toolbar
    import mimetypes

    mimetypes.add_type("application/javascript", ".js", True)
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
