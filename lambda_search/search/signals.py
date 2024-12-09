from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from search.models import ManagedDatabase

__all__ = ()


@receiver(post_migrate)
def update_databases(sender, **kwargs):
    """Обновление баз данных при запуске Django."""
    active_dbs = ManagedDatabase.objects.filter(active=True)
    for db in active_dbs:
        settings.DATABASES[db.name] = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db.path,
        }
