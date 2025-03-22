from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from feedback.forms import FeedbackForm, FilesForm, UserForm
from feedback.models import FeedbackFile, StatusLog, UserInfo
from users.models import User

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
            mail = user_form.cleaned_data.get("mail")

            if request.user.is_authenticated:
                user = request.user
            else:
                feedback.save()
                user = User.objects.create_user(
                    username="anonymous_" + str(feedback.id),
                    email=mail,
                    password=None,
                )

            if not feedback.pk:
                feedback.save()

            user_info = UserInfo.objects.create(
                name=user_form.cleaned_data.get("name"),
                mail=mail,
                user_info=feedback,
                user=user,
            )
            feedback.author = user_info
            feedback.save()

            StatusLog.objects.create(
                feedback=feedback,
                from_status="",
                to=feedback.status,
            )

            if request.FILES.getlist("files"):
                for f in request.FILES.getlist("files"):
                    FeedbackFile.objects.create(
                        feedback=feedback,
                        file=f,
                    )

            messages.success(request, "Форма успешно отправлена!")
            return redirect("feedback:feedback")

        context = {
            "form": form,
            "user_form": user_form,
            "file_form": file_form,
        }
        return render(request, self.template_name, context)
