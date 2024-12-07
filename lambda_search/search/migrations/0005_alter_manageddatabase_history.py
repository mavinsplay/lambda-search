# Generated by Django 4.2.16 on 2024-12-06 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0004_alter_manageddatabase_history"),
    ]

    operations = [
        migrations.AlterField(
            model_name="manageddatabase",
            name="history",
            field=models.TextField(
                help_text="Краткая история об утечке (не более 500 символов)",
                max_length=500,
                null=True,
                verbose_name="История",
            ),
        ),
    ]
