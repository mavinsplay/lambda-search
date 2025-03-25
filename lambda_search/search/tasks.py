from pathlib import Path

from celery import shared_task
from django.conf import settings

from search.encryptor import UnifiedEncryptor
from search.models import ManagedDatabase

__all__ = ()


@shared_task(bind=True)
def encrypt_database_task(self, db_id):
    try:
        db_obj = ManagedDatabase.objects.get(pk=db_id)
    except ManagedDatabase.DoesNotExist:
        # Если объект не найден, пробуем подождать немного и повторить
        from time import sleep

        sleep(5)  # Ждем 5 секунд
        try:
            db_obj = ManagedDatabase.objects.get(pk=db_id)
        except ManagedDatabase.DoesNotExist:
            return {
                "error": "База данных не найдена",
                "processed": 0,
                "total": 0,
                "percent": 0,
            }

    try:
        key = settings.ENCRYPTION_KEY
        encryptor = UnifiedEncryptor(key, file_path=Path(db_obj.file.path))

        handler = encryptor.handler
        total_rows = handler.count_rows()
        if total_rows <= 0:
            total_rows = 1

        def progress_callback(processed):
            percent = int((processed / total_rows) * 100)
            self.update_state(
                state="PROGRESS",
                meta={
                    "processed": processed,
                    "total": total_rows,
                    "percent": percent,
                },
            )

        encryptor.encrypt_database_cells(progress_callback=progress_callback)

        db_obj.is_encrypted = True
        db_obj.save(update_fields=["is_encrypted"])

        return {"processed": 100, "total": 100, "percent": 100}

    except Exception as e:
        return {
            "error": str(e),
            "processed": 0,
            "total": 0,
            "percent": 0,
        }
