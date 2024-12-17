import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

__all__ = ()


class Command(BaseCommand):

    load_dotenv()

    def handle(self, *args, **options):
        superuser_name = os.getenv("LAMBDA_SUPERUSER_NAME", "admin")
        superuser_email = os.getenv(
            "LAMBDA_SUPERUSER_EMAIL", "admin@lambda-search.ru",
        )
        superuser_password = os.getenv(
            "LAMBDA_SUPERUSER_PASSWORD", "4pNWn0;3(!6zKka7B74H",
        )

        if not get_user_model().objects.filter(username=superuser_name).exists():
            get_user_model().objects.create_superuser(
                username=superuser_name,
                email=superuser_email,
                password=superuser_password,
            )

            self.stdout.write(
                self.style.SUCCESS("Superuser created successfully!"),
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Superuser already exist!"),
            )



