from django.conf import settings
from django.contrib import messages
import django.contrib.auth
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views import View
from django.views.generic import DetailView, FormView, ListView

import users.forms
from users.models import Profile

__all__ = ()


class UserListView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.filter(is_active=True)


class UserDetailView(DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "user"
    pk_url_kwarg = "user_id"


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except Exception:
            messages.error(request, _("Account Error"))


class ActivateUserView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        now = timezone.now()

        if not user.profile.date_last_active:
            time_difference = now - user.date_joined
            allowed_activation_time = 12
        else:
            time_difference = now - user.profile.date_last_active
            allowed_activation_time = 168

        datediff = int(time_difference.total_seconds() // 3600)

        if not user.is_active:
            if datediff <= allowed_activation_time:
                user.is_active = True
                user.save()
                messages.success(
                    request,
                    _("User successfully activated"),
                )
                django.contrib.auth.login(request, user)
                return redirect(reverse("homepage:homepage"))

            messages.error(
                request,
                _(
                    "Profile activation was available for"
                    f" {allowed_activation_time} hours after registration",
                ),
            )
        else:
            messages.error(request, _("User is already activated"))

        return redirect(reverse("users:login"))


class SignupView(FormView):
    template_name = "users/signup.html"
    form_class = users.forms.SignUpForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = users.models.UserManager().normalize_email(
            form.cleaned_data["email"],
        )
        user.is_active = settings.DEFAULT_USER_IS_ACTIVE
        user.save()
        Profile.objects.create(user=user)
        self.send_activation_email(user)
        return redirect("users:login")

    @staticmethod
    def send_activation_email(user):
        activation_link = f"{settings.SITE_URL}/auth/activate/{user.username}"
        send_mail(
            "Activate your account",
            ("Follow the link to activate" f" account: {activation_link}"),
            settings.MAIL,
            [user.email],
        )


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = users.forms.UserChangeForm(instance=request.user)
        profile_form = users.forms.UserProfileForm(
            instance=request.user.profile,
        )
        return render(
            request,
            "users/profile.html",
            {"form": form, "profile_form": profile_form},
        )

    def post(self, request):
        form = users.forms.UserChangeForm(request.POST, instance=request.user)
        profile_form = users.forms.UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
        )
        if profile_form.is_valid():
            profile_form.save()
            return redirect("users:profile")

        if form.is_valid():
            user_form = form.save(commit=False)
            user_form.mail = users.models.UserManager().normalize_email(
                form.cleaned_data["email"],
            )
            user_form.save()
            profile_form.save()
            messages.success(
                request,
                _("The form has been successfully submitted!"),
            )
            return redirect("users:profile")

        return render(
            request,
            "users/profile.html",
            {"form": form, "profile_form": profile_form},
        )
