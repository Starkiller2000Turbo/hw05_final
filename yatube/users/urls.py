from django.contrib.auth import views
from django.urls import include, path

from users.views import SignUp

app_name = '%(app_label)s'

passwords = [
    path(
        'change/done/',
        views.PasswordChangeDoneView.as_view(),
        name='pass_change_done',
    ),
    path(
        'change/',
        views.PasswordChangeView.as_view(),
        name='pass_change',
    ),
    path(
        'reset/done/',
        views.PasswordResetDoneView.as_view(),
        name='pass_reset_done',
    ),
    path('reset/', views.PasswordResetView.as_view(), name='pass_reset'),
    path(
        'reset/complete/',
        views.PasswordResetCompleteView.as_view(),
        name='pass_reset_complete',
    ),
    path(
        'reset/<uidb64>/<token>',
        views.PasswordResetConfirmView.as_view(),
        name='pass_reset_confirm',
    ),
]

urlpatterns = [
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', SignUp.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('passwords/', include(passwords)),
]
