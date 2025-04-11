from django.forms import ClearableFileInput

__all__ = ()


class ProgressBarFileInput(ClearableFileInput):
    template_name = "admin/widgets/progress_file_input.html"

    class Media:
        js = ("js/file_upload_progress.js",)
        css = {"all": ("css/file_upload_progress.css",)}
