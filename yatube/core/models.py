from behaviors.behaviors import Timestamped
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class DefaultModel(models.Model):
    class Meta:
        abstract = True


class TimestampedModel(DefaultModel, Timestamped):
    class Meta:
        abstract = True


class TextModel(TimestampedModel):
    """Модель с текстом и автором."""

    author = models.ForeignKey(
        User,
        verbose_name='автор',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='текст',
        help_text='Введите текст',
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.text[:settings.TEXT_LENGTH]  # fmt: skip
