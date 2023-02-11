from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Timestamped(models.Model):
    """
    An abstract behavior representing timestamping a model with``created`` and
    ``modified`` fields.
    """

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    @property
    def changed(self) -> bool:
        return True if self.modified else False

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            self.modified = timezone.now()
        return super().save(*args, **kwargs)


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
