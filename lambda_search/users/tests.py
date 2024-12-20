from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from users.models import Profile

User = get_user_model()

__all__ = ()


class UserManagerTest(TestCase):
    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "Test.User+tag@yandex.ru",
            "password": "password123",
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_normalize_email(self):
        normalized_email = User.objects.normalize_email(self.user.email)
        self.assertEqual(normalized_email, "Test.User+tag@yandex.ru")

    def test_active_users(self):
        active_user = User.objects.create_user(
            username="activeuser",
            email="active@example.com",
            password="password",
        )
        inactive_user = User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="password",
            is_active=False,
        )

        active_users = User.objects.filter(is_active=True)
        self.assertIn(active_user, active_users)
        self.assertNotIn(inactive_user, active_users)


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="password123",
        )
        self.profile = Profile.objects.create(user=self.user)

    def test_profile_creation(self):
        self.assertIsNotNone(self.profile.id)
        self.assertEqual(self.profile.user, self.user)

    def test_profile_image_field(self):
        self.profile.image = "users/images/test_image.jpg"
        self.profile.save()

        self.assertEqual(
            self.profile.image.name,
            "users/images/test_image.jpg",
        )

    def test_attempts_count_default(self):
        self.assertEqual(self.profile.attempts_count, 0)

    def test_date_last_active(self):
        from django.utils import timezone

        now = timezone.now()
        self.profile.date_last_active = now
        self.profile.save()

        self.assertEqual(self.profile.date_last_active, now)


class UserViewsTest(TestCase):

    def setUp(self):
        self.user_data = {
            "username": "testuser",
            "email": "test.user+tag@yandex.ru",
            "password": "password123",
        }
        self.user = User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"],
        )

    def test_login_view(self):
        response = self.client.post(
            reverse("users:login"),
            data={"username": self.user.username, "password": "password123"},
        )
        self.assertEqual(response.status_code, 302)

    def test_signup_view(self):
        signup_data = {
            "username": "newuser",
            "email": "new.user@example.com",
            "password1": "newpassword123",
            "password2": "newpassword123",
        }
        response = self.client.post(reverse("users:signup"), data=signup_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_profile_view_get(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse("users:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")

    def test_profile_view_post(self):
        self.client.login(username="testuser", password="password123")

        new_data = {
            "email": "newemail@example.com",
            "first_name": "NewFirstName",
            "last_name": "NewLastName",
        }

        response = self.client.post(reverse("users:profile"), data=new_data)

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.first_name, "NewFirstName")
        self.assertEqual(self.user.email, "newemail@example.com")

    def test_invalid_signup_form(self):
        invalid_data = {
            "username": "",
            "email": "invalidemail",
            "password1": "password123",
            "password2": "differentpassword",
        }

        response = self.client.post(reverse("users:signup"), data=invalid_data)

        self.assertEqual(response.status_code, 200)
