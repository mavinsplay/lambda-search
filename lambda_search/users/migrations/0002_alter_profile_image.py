# Generated by Django 4.2.16 on 2024-12-09 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="image",
            field=models.ImageField(
                blank=True,
                help_text="Upload a profile picture",
                null=True,
                upload_to="users/images/",
                verbose_name="путь к изображению профиля",
            ),
        ),
    ]