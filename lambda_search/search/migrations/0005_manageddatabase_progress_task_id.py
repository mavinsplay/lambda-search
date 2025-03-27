# Generated by Django 4.2.16 on 2025-03-26 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0004_remove_manageddatabase_progress_task_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="manageddatabase",
            name="progress_task_id",
            field=models.CharField(
                blank=True,
                max_length=255,
                null=True,
                verbose_name="ID задачи шифрования",
            ),
        ),
    ]
