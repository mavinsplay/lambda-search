__all__ = []

import datetime
import http

import django.contrib.auth.models
import django.contrib.messages
import django.test
import django.urls
import django.utils
import django.utils.timezone
import parametrize

import users.models
import users

user_model = django.contrib.auth.models.User


class SignupTest(django.test.TestCase):
    def test_corrcet_create_new_user(self):
        data = {
            "username": "TestUserName",
            "email": "testemail@mail.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        users.forms.SignUpForm(data).save()
        count_models = user_model.objects.all().count()
        self.assertEqual(count_models, 1)

    def test_create_user_not_equal_passwords(self):
        data = {
            "username": "TestUserName",
            "email": "testemail@mail.com",
            "password1": "testpassword123",
            "password2": "testpassword1234567890",
        }
        response = self.client.post(django.urls.reverse("users:signup"), data)
        count_models = user_model.objects.all().count()
        self.assertTrue(response.context["form"].has_error("password2"))
        self.assertEqual(count_models, 0)

    def test_create_user_name_exists(self):
        data1 = {
            "username": "TestUserName",
            "email": "testemail@mail.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }

        data2 = {
            "username": "TestUserName",
            "email": "testemail2@mail.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }

        self.client.post(django.urls.reverse("users:signup"), data1)
        response = self.client.post(django.urls.reverse("users:signup"), data2)
        count_models = user_model.objects.all().count()

        self.assertTrue(response.context["form"].has_error("username"))
        self.assertEqual(count_models, 1)

    def test_create_users_profile(self):
        data = {
            "username": "TestUserName2",
            "email": "testemail@mail.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
        }
        self.client.post(django.urls.reverse("users:signup"), data)
        count_models = users.models.Profile.objects.all().count()
        self.assertEqual(count_models, 1)


class ActivateUserTest(django.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        user_model = django.contrib.auth.models.User

        cls.not_active_data = {
            "username": "TestNotActiveUserName",
            "email": "testemail1@mail.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
            "is_active": False,
        }

        cls.user_not_active = user_model.objects.create_user(
            username=cls.not_active_data["username"],
            email=cls.not_active_data["email"],
            password=cls.not_active_data["password1"],
            is_active=cls.not_active_data["is_active"],
        )

        users.models.Profile.objects.create(
            user=cls.user_not_active
        )

        cls.data_active = {
            "username": "TestActiveUserName",
            "email": "testemail2@mail.com",
            "password1": "testpassword123",
            "password2": "testpassword123",
            "is_active": True,
        }

        cls.user_active = user_model.objects.create_user(
            username=cls.data_active["username"],
            email=cls.data_active["email"],
            password=cls.data_active["password1"],
            is_active=cls.data_active["is_active"],
        )

        users.models.Profile.objects.create(user=cls.user_active)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        cls.user_not_active.delete()
        cls.user_active.delete()

    def test_not_activate_user(self):
        response = self.client.get(
            django.urls.reverse(
                "users:activate",
                args=["TestNotActiveUserName"],
            ),
        )
        messages = list(
            django.contrib.messages.get_messages(response.wsgi_request),
        )

        self.assertTrue(
            any(
                "Пользователь успешно активирован" in str(m) for m in messages
            ),
        )

    def test_active_user(self):
        response = self.client.get(
            django.urls.reverse(
                "users:activate",
                args=["TestActiveUserName"],
            ),
        )
        messages = list(
            django.contrib.messages.get_messages(response.wsgi_request),
        )

        self.assertTrue(
            any("Пользователь уже активирован" in str(m) for m in messages),
        )

    def test_not_real_user(self):
        response = self.client.get(
            django.urls.reverse("users:activate", args=["NotRealUSer"]),
        )
        self.assertEqual(response.status_code, http.HTTPStatus.NOT_FOUND)


class TestAuthinicateUser(django.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        model = django.contrib.auth.models.User
        cls.user = model.objects.create_user(
            username="TestUser",
            email="testemail@mail.com",
            password="Testpassword123",
        )
        cls.profile = users.models.Profile.objects.create(
            user=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.user.delete()

    @parametrize.parametrize(
        "username,password",
        [
            ("TestUser", "Testpassword123"),
        ],
    )
    def test_login_user(self, username, password):
        data = {
            "username": username,
            "password": password,
        }
        response = self.client.post(django.urls.reverse("users:login"), data)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_wrong_password_login_user(self):
        data = {
            "username": "TestUser",
            "password": "WrongPassword123",
        }
        response = self.client.post(django.urls.reverse("users:login"), data)

        self.assertFalse(response.wsgi_request.user.is_authenticated)


class NormalEmailTests(django.test.TestCase):

    def test_has_user_mail_normal_form(self):
        data = {
            "email": "test.mail@ya.ru",
            "username": "TestLogin123456",
            "password1": "Testpassword123",
            "password2": "Testpassword123",
        }
        self.client.post(django.urls.reverse("users:signup"), data)
        user = user_model.objects.get(username="TestLogin123456")
        self.assertEqual(user.email, "test-mail@yandex.ru")

    @django.test.override_settings(MAX_AUTH_ATTEMPTS=5)
    def lock_user_after_some_failed_attempts(self):
        data = {
            "email": "test.mail@ya.ru",
            "username": "TestLogin123456",
            "password1": "Testpassword123",
            "password2": "Testpassword123",
        }
        self.client.post(django.urls.reverse("users:signup"), data)
        user = user_model.objects.get(username="TestLogin123456")

        for _ in range(5):
            self.client.post(
                django.urls.reverse("users:login"),
                {"username": "TestLogin123456", "password": "wrongpassword"},
            )

        self.assertFa(user.is_active)

    def test_corrcet_activate_user_after_lock(self):
        data = {
            "email": "test.mail@ya.ru",
            "username": "TestLogin123456",
            "password": "Testpassword123",
        }

        user = users.models.User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            is_active=False,
        )
        user = users.models.User.objects.get(
            username=user.username
        )
        users.models.Profile.objects.create(
            user=user,
            date_last_active=django.utils.timezone.now()
            - datetime.timedelta(days=1),
        )
        response = self.client.get(
            django.urls.reverse("users:activate", args=[user.username]),
        )

        messages = list(
            django.contrib.messages.get_messages(response.wsgi_request),
        )

        self.assertTrue(
            any(
                "Пользователь успешно активирован" in str(m) for m in messages
            ),
        )

    def test_uncorrcet_activate_user_after_lock(self):
        data = {
            "email": "test.mail@ya.ru",
            "username": "TestLogin123456",
            "password": "Testpassword123",
        }

        user = users.models.User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            is_active=False,
        )
        user = users.models.User.objects.get(
            username=user.username
        )
        users.models.Profile.objects.create(
            user=user,
            date_last_active=django.utils.timezone.now()
            - datetime.timedelta(days=8),
        )
        response = self.client.get(
            django.urls.reverse("users:activate", args=[user.username]),
        )

        messages = list(
            django.contrib.messages.get_messages(response.wsgi_request),
        )

        self.assertTrue(
            any(
                "Активация профиля была доступна в течение" in str(m)
                for m in messages
            ),
        )
