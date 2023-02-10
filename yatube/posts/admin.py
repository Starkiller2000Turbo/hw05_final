from django.contrib import admin

from core.admin import BaseAdmin
from posts.models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(BaseAdmin):
    """Способ отображения поста в админке."""

    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('created',)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    """Способ отображения группы в админке."""

    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    search_fields = ('description',)
    list_filter = ('title',)


@admin.register(Comment)
class CommentAdmin(BaseAdmin):
    """Способ отображения комментария в админке."""

    list_display = (
        'pk',
        'post',
        'author',
        'text',
    )
    search_fields = ('text',)
    list_filter = ('author',)


@admin.register(Follow)
class FollowAdmin(BaseAdmin):
    """Способ отображения подписки в админке."""

    list_display = (
        'pk',
        'user',
        'author',
    )
    list_filter = (
        'user',
        'author',
    )
