from behaviors.behaviors import Timestamped
from django.db import models


class DefaultModel(models.Model):
    class Meta:
        abstract = True


class TimestampedModel(DefaultModel, Timestamped):
    class Meta:
        abstract = True
