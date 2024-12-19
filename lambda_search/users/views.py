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


def vigenere_encode(plaintext, key):
    key = key.lower()
    key_length = len(key)

    encrypted_text = []

    key_index = 0

    for char in plaintext:
        if char.isalpha():
            shift = ord(key[key_index % key_length]) - ord("a")
            if char.islower():
                encrypted_char = chr(
                    (ord(char) - ord("a") + shift) % 26 + ord("a"),
                )
            else:
                encrypted_char = chr(
                    (ord(char) - ord("A") + shift) % 26 + ord("A"),
                )

            encrypted_text.append(encrypted_char)
            key_index += 1
        else:
            caesar_shift = 13
            encrypted_digit = int(char) + caesar_shift
            encrypted_text.append(str(encrypted_digit))

    return "".join(encrypted_text)


def vigenere_decode(encrypted_text, key):
    key = key.lower()
    key_length = len(key)

    decrypted_text = []

    key_index = 0

    for char in encrypted_text:
        if char.isalpha():
            shift = ord(key[key_index % key_length]) - ord("a")
            if char.islower():
                decrypted_char = chr(
                    (ord(char) - ord("a") + shift) % 26 + ord("a"),
                )
            else:
                decrypted_char = chr(
                    (ord(char) - ord("A") + shift) % 26 + ord("A"),
                )

            decrypted_text.append(decrypted_char)
            key_index += 1
        else:
            caesar_shift = 13
            decrypted_digit = int(char) - caesar_shift
            decrypted_text.append(str(decrypted_digit))

    return "".join(decrypted_text)


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
        key = "lamda_search"
        user = get_object_or_404(
            User,
            username=vigenere_decode(
                username,
                key * (len(username) // len(key))
                + key[: len(username) % len(key)],
            ),
        )
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
        key = "lamda_search"

        path = vigenere_encode(
            user.username,
            key * (len(user.username) // len(key))
            + key[: len(user.username) % len(key)],
        )

        activation_link = f"{settings.SITE_URL}/auth/activate/{path}"
        print(users.models.UserManager().normalize_email(user.email))
        send_mail(
            "Activate your account",
            ("Follow the link to activate" f" account: {activation_link}"),
            settings.MAIL,
            [users.models.UserManager().normalize_email(user.email)],
        )


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        form = users.forms.UserChangeForm(instance=request.user)
        try:
            request.user.profile
        except Exception:
            Profile.objects.create(user=request.user)

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
        try:
            request.user.profile
        except Exception:
            Profile.objects.create(user=request.user)

        profile_form = users.forms.UserProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.profile,
        )

        try:
            if form.is_valid():
                user_form = form.save(commit=False)
                if form.cleaned_data["email"]:
                    user_form.mail = users.models.UserManager().normalize_email(
                        form.cleaned_data["email"],
                    )

                user_form.save()

                messages.success(
                    request,
                    _("The form has been successfully submitted!"),
                )
                return redirect("users:profile")

        except Exception as ex:
            print(ex)

        try:
            if profile_form.is_valid():
                new_profile_form = profile_form.save(commit=False)
                new_profile_form.image = profile_form.cleaned_data["image"]

                new_profile_form.save()
        
            messages.success(
                request,
                _("The form has been successfully submitted!"),
            )
            return redirect("users:profile")
        
        except Exception as ex:
            print(ex)


        return render(
            request,
            "users/profile.html",
            {"form": form, "profile_form": profile_form},
        )
