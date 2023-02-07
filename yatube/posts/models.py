from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    """Модель группы."""

    title: models.CharField = models.CharField(
        max_length=200,
        verbose_name='заголовок',
    )
    slug: models.SlugField = models.SlugField(unique=True, verbose_name='путь')
    description: models.TextField = models.TextField(verbose_name='описание')

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    """Модель поста."""

    text: models.TextField = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    group: models.ForeignKey = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='Группа',
        help_text='Выберите группу',
    )
    image: models.ImageField = models.ImageField(
        verbose_name='Картинка',
        help_text='Выберите картинку',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.text[:settings.TEXT_LENGTH]  # fmt: skip


class Comment(CreatedModel):
    """Модель группы."""

    post: models.ForeignKey = models.ForeignKey(
        Post,
        verbose_name='Пост',
        on_delete=models.CASCADE,
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    text: models.TextField = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'comments'

    def __str__(self) -> str:
        return self.text[:settings.TEXT_LENGTH]  # fmt: skip


class Follow(models.Model):
    """Модель подписки."""

    user: models.ForeignKey = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE,
    )
