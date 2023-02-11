from django.contrib.auth import get_user_model
from django.db import models

from core.models import DefaultModel, TextModel

User = get_user_model()


class Group(DefaultModel):
    """Модель группы."""

    title = models.CharField(
        max_length=200,
        verbose_name='заголовок',
    )
    slug = models.SlugField(unique=True, verbose_name='путь')
    description = models.TextField(verbose_name='описание')

    def __str__(self) -> str:
        return self.title


class Post(TextModel):
    """Модель поста."""

    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        verbose_name='картинка',
        help_text='Выберите картинку',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'posts'


class Comment(TextModel):
    """Модель группы."""

    post = models.ForeignKey(
        Post,
        verbose_name='пост',
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('-created',)
        default_related_name = 'comments'


class Follow(DefaultModel):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        related_name='following',
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f'подписка {self.user} на {self.author}'
