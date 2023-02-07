from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import include, path

from users import apps, views

app_name = apps.UsersConfig.name

passwords = [
    path(
        'change/done/',
        PasswordChangeDoneView.as_view(),
        name='pass_change_done',
    ),
    path(
        'change/',
        PasswordChangeView.as_view(),
        name='pass_change',
    ),
    path(
        'reset/done/',
        PasswordResetDoneView.as_view(),
        name='pass_reset_done',
    ),
    path('reset/', PasswordResetView.as_view(), name='pass_reset'),
    path(
        'reset/complete/',
        PasswordResetCompleteView.as_view(),
        name='pass_reset_complete',
    ),
    path(
        'reset/<uidb64>/<token>',
        PasswordResetConfirmView.as_view(),
        name='pass_reset_confirm',
    ),
]

urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('passwords/', include(passwords)),
]
