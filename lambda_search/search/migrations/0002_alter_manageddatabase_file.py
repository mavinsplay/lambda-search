# Generated by Django 4.2.16 on 2024-12-16 18:12

import django.core.validators
from django.db import migrations, models

import search.models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="manageddatabase",
            name="file",
            field=models.FileField(
                blank=True,
                upload_to=search.models.database_upload_path,
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["csv", "sqlite", "db"]
                    )
                ],
                verbose_name="Файл базы данных",
            ),
        ),
    ]
