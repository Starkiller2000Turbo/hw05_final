# Generated by Django 2.2.16 on 2023-02-05 09:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0007_auto_20230203_1521'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Выберите картинку',
                upload_to='posts/',
                verbose_name='Картинка',
            ),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'text',
                    models.TextField(
                        help_text='Введите текст комментария',
                        verbose_name='Текст комментария',
                    ),
                ),
                (
                    'created',
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name='Дата и время публикации',
                    ),
                ),
                (
                    'author',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='comments',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Автор',
                    ),
                ),
                (
                    'post',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='comments',
                        to='posts.Post',
                        verbose_name='Пост',
                    ),
                ),
            ],
            options={
                'ordering': ('-created',),
                'default_related_name': 'comments',
            },
        ),
    ]
