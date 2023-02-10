from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from core.models import DefaultModel, TimestampedModel

User = get_user_model()


class Group(DefaultModel):
    """Модель группы."""

    title: models.CharField = models.CharField(
        max_length=200,
        verbose_name='заголовок',
    )
    slug: models.SlugField = models.SlugField(unique=True, verbose_name='путь')
    description: models.TextField = models.TextField(verbose_name='описание')

    def __str__(self) -> str:
        return self.title


class Post(TimestampedModel):
    """Модель поста."""

    text: models.TextField = models.TextField(
        verbose_name='текст поста',
        help_text='Введите текст поста',
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
    )
    group: models.ForeignKey = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Выберите группу',
    )
    image: models.ImageField = models.ImageField(
        verbose_name='картинка',
        help_text='Выберите картинку',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'posts'

    def __str__(self) -> str:
        return self.text[:settings.TEXT_LENGTH]  # fmt: skip


class Comment(TimestampedModel):
    """Модель группы."""

    post: models.ForeignKey = models.ForeignKey(
        Post,
        verbose_name='пост',
        on_delete=models.CASCADE,
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
    )
    text: models.TextField = models.TextField(
        verbose_name='текст комментария',
        help_text='Введите текст комментария',
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'comments'

    def __str__(self) -> str:
        return self.text[:settings.TEXT_LENGTH]  # fmt: skip


class Follow(DefaultModel):
    """Модель подписки."""

    user: models.ForeignKey = models.ForeignKey(
        User,
        verbose_name='пользователь',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author: models.ForeignKey = models.ForeignKey(
        User,
        verbose_name='автор',
        related_name='following',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f'подписка {self.user} на {self.author}'
