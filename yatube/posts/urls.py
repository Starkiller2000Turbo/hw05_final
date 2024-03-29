from django.urls import path

from posts import views

app_name = '%(app_label)s'

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.post_create, name='post_create'),
    path('group/<str:slug>/', views.group_posts, name='group_list'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow',
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow',
    ),
    path('profile/<str:username>/', views.profile, name='profile'),
    path(
        'posts/<int:pk>/comment/',
        views.add_comment,
        name='add_comment',
    ),
    path('posts/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),
    path('follow/', views.follow_index, name='follow_index'),
]
