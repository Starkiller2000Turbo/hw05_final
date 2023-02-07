# Generated by Django 2.2.16 on 2023-02-06 10:59

import datetime

from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0008_auto_20230205_1205'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={
                'default_related_name': 'posts',
                'ordering': ('-created',),
            },
        ),
        migrations.RemoveField(
            model_name='post',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='post',
            name='created',
            field=models.DateTimeField(
                auto_now_add=True,
                default=datetime.datetime(
                    2023, 2, 6, 10, 59, 36, 510481, tzinfo=utc
                ),
                verbose_name='Дата создания',
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(
                auto_now_add=True, verbose_name='Дата создания'
            ),
        ),
    ]