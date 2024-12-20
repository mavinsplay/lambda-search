from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from feedback.forms import FeedbackForm, FilesForm, UserForm
from feedback.models import StatusLog, UserInfo

__all__ = ()


class FeedbackView(View):
    template_name = "feedback/feedback.html"

    def get(self, request):
        context = {
            "form": FeedbackForm(),
            "user_form": UserForm(),
            "file_form": FilesForm(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = FeedbackForm(request.POST or None)
        user_form = UserForm(request.POST or None)
        file_form = FilesForm(request.POST or None, request.FILES)

        if form.is_valid() and user_form.is_valid() and file_form.is_valid():
            feedback = form.save(commit=False)
            feedback.save()

            mail = user_form.cleaned_data.get("mail")

            UserInfo.objects.create(
                name=form.cleaned_data.get("name"),
                mail=mail,
                user_info=feedback,
            )

            StatusLog.objects.create(
                feedback=feedback,
                from_status="",
                to=feedback.status,
            )

            messages.success(request, "Форма успешно отправлена!")
            return redirect("feedback:feedback")

        context = {
            "form": form,
            "user_form": user_form,
            "file_form": file_form,
        }
        return render(request, self.template_name, context)
