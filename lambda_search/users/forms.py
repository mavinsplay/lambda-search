from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from captcha.fields import CaptchaField

from users.models import Profile

__all__ = ()


class BootstrapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.widget.attrs["class"] = "form-control"


class UserChangeForm(BootstrapForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.required = False

    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            model.email.field.name,
            model.first_name.field.name,
            model.last_name.field.name,
        )


class SignUpForm(UserCreationForm):
    captcha = CaptchaField()

    class Meta(UserCreationForm.Meta):
        fields = (
            UserChangeForm.Meta.model.email.field.name,
            UserChangeForm.Meta.model.username.field.name,
            "password1",
            "password2",
        )
        labels = {
            UserChangeForm.Meta.model.username.field.name: _(
                "Enter your login",
            ),
        }


class UserProfileForm(BootstrapForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.visible_fields():
            field.field.required = False

    class Meta:
        model = Profile
        fields = (Profile.image.field.name,)

        labels = {
            Profile.image.field.name: _("Choose your picture"),
        }
