# Generated by Django 4.2.16 on 2024-12-15 16:50

import django.db.models.deletion
from django.db import migrations, models

import search.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ManagedDatabase",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255,
                        unique=True,
                        verbose_name="Имя базы данных",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        blank=True,
                        upload_to=search.models.database_upload_path,
                        verbose_name="Файл базы данных",
                    ),
                ),
                (
                    "history",
                    models.TextField(
                        blank=True,
                        default="История об этой базе не найдена",
                        help_text="Краткая история об утечке (не более 500 символов)",
                        max_length=500,
                        null=True,
                        verbose_name="История",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=False,
                        help_text="Определяет, используется ли эта база данных",
                        verbose_name="Активна",
                    ),
                ),
                (
                    "is_encrypted",
                    models.BooleanField(
                        default=False, verbose_name="Зашифрована"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        null=True,
                        verbose_name="Дата создания",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        null=True,
                        verbose_name="Дата обновления",
                    ),
                ),
            ],
            options={
                "verbose_name": "База данных",
                "verbose_name_plural": "Базы данных",
            },
        ),
        migrations.CreateModel(
            name="Data",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user_index",
                    models.IntegerField(verbose_name="Индекс пользователя"),
                ),
                (
                    "column_name",
                    models.CharField(
                        max_length=255, verbose_name="Название колонки"
                    ),
                ),
                (
                    "value",
                    models.CharField(max_length=255, verbose_name="Значение"),
                ),
                (
                    "database",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="data",
                        to="search.manageddatabase",
                        verbose_name="Имя базы данных",
                    ),
                ),
            ],
            options={
                "verbose_name": "Данные",
                "verbose_name_plural": "Данные",
                "unique_together": {
                    ("database", "user_index", "column_name", "value")
                },
            },
        ),
    ]
