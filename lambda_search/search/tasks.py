from pathlib import Path

from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.conf import settings

from search.encryptor import UnifiedEncryptor
from search.models import ManagedDatabase

__all__ = ()


@shared_task(bind=True)
def encrypt_database_task(self, db_id):
    try:
        db_obj = ManagedDatabase.objects.get(pk=db_id)
        if not db_obj.is_encrypted:
            db_obj.progress_task_id = self.request.id
            ManagedDatabase.objects.filter(pk=db_id).update(
                progress_task_id=self.request.id,
            )

            progress_recorder = ProgressRecorder(self)

            progress_recorder.set_progress(
                0,
                100,
                "The beginning of encryption...",
            )

            key = settings.ENCRYPTION_KEY
            encryptor = UnifiedEncryptor(key, file_path=Path(db_obj.file.path))

            handler = encryptor.handler
            total_rows = handler.count_rows()

            def progress_callback(processed):
                percent = int((processed / total_rows) * 100)
                progress_recorder.set_progress(
                    processed,
                    total_rows,
                    f"Processed {processed} \
                        of {total_rows} records ({percent}%)",
                )

            encryptor.encrypt_database_cells(
                progress_callback=progress_callback,
            )

            progress_recorder.set_progress(
                total_rows,
                total_rows,
                "Encryption is complete",
            )

            ManagedDatabase.objects.filter(pk=db_id).update(
                is_encrypted=True,
                encryption_started=False,
            )
            if Path(db_obj.file.path).exists():
                Path(db_obj.file.path).unlink()

            return {
                "current": total_rows,
                "total": total_rows,
                "percent": 100,
                "description": "The task is completed!",
            }

    except Exception as e:
        ManagedDatabase.objects.filter(pk=db_id).update(
            encryption_started=False,
        )
        return {
            "current": 0,
            "total": 100,
            "percent": 0,
            "description": f"Error: {str(e)}",
        }
