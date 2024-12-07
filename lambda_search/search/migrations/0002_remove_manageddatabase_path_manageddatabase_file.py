# Generated by Django 4.2.16 on 2024-12-03 19:12

from django.db import migrations, models

import search.models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="manageddatabase",
            name="path",
        ),
        migrations.AddField(
            model_name="manageddatabase",
            name="file",
            field=models.FileField(
                default="def",
                upload_to=search.models.database_upload_path,
                verbose_name="Файл базы данных",
            ),
            preserve_default=False,
        ),
    ]
