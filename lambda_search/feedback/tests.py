import tempfile

import django.core.files.uploadedfile
import django.test
import django.urls

from feedback.models import Feedback, FeedbackFile, StatusLog

__all__ = ()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@django.test.override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FeedbackContextTests(django.test.TestCase):
    def test_form_context(self):
        response = django.test.Client().get(
            django.urls.reverse("feedback:feedback"),
        )
        self.assertIn(
            "form",
            response.context,
            "Feedback form should be in context",
        )

    def test_true_mail_label_and_help_text(self):
        response = django.test.Client().get(
            django.urls.reverse("feedback:feedback"),
        )
        form = response.context["user_form"]
        self.assertEqual(form.fields["mail"].label, "Почта")
        self.assertEqual(
            form.fields["mail"].help_text,
            "Введите вашу почту",
        )

    def test_true_name_label_and_help_text(self):
        response = django.test.Client().get(
            django.urls.reverse("feedback:feedback"),
        )
        form = response.context["user_form"]
        self.assertEqual(form.fields["name"].label, "Имя")
        self.assertEqual(form.fields["name"].help_text, "Введите ваше имя")

    def test_true_text_label_and_help_text(self):
        response = django.test.Client().get(
            django.urls.reverse("feedback:feedback"),
        )
        form = response.context["form"]
        self.assertEqual(form.fields["text"].label, "Отзыв")
        self.assertEqual(form.fields["text"].help_text, "Напишите ваш отзыв")

    def test_unable_create_feedback(self):
        form_data = {
            "name": "Тест",
            "text": "Тест",
            "mail": "notmail",
        }

        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=form_data,
            follow=True,
        )
        self.assertTrue(response.context["user_form"].has_error("mail"))

    def test_create_feedback(self):
        form_data = {
            "name": "Тест",
            "text": "Тест",
            "mail": "123@l.com",
        }

        response = django.test.Client().post(
            django.urls.reverse("feedback:feedback"),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            django.urls.reverse("feedback:feedback"),
        )

    def test_feedback_creation_and_status_log(self):
        _ = self.client.post(
            django.urls.reverse("feedback:feedback"),
            {
                "name": "Тестовое имя",
                "mail": "test@example.com",
                "text": "Тестовое сообщение",
            },
        )

        feedback = Feedback.objects.get(text="Тестовое сообщение")
        self.assertEqual(feedback.status, "received")

        status_log = StatusLog.objects.get(feedback=feedback)
        self.assertEqual(status_log.from_status, "")
        self.assertEqual(status_log.to, "received")

    def test_feedback_creation(self):
        _ = self.client.post(
            django.urls.reverse("feedback:feedback"),
            {
                "name": "Тестовое имя",
                "mail": "test@example.com",
                "text": "Тестовое сообщение",
            },
        )

        self.assertEqual(Feedback.objects.count(), 1)

    def test_feedback(self):
        test_file = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test_file.txt",
            content=b"This is a test file content.",
            content_type="text/plain",
        )

        form_data = {
            "text": "This is a feedback text.",
            "mail": "test@example.com",
            "name": "Test User",
        }
        file_data = {"files": [test_file]}

        response = self.client.post(
            django.urls.reverse("feedback:feedback"),
            data={**form_data, **file_data},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Форма успешно отправлена!")

    def test_feedback_upload(self):
        test_file = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test_file1.txt",
            content=b"This is a test file content.",
            content_type="text/plain",
        )
        form_data = {
            "text": "This is a feedback text.",
            "mail": "test@example.com",
            "name": "Test User",
        }

        file_data = {"files": [test_file]}

        _ = self.client.post(
            django.urls.reverse("feedback:feedback"),
            data={**form_data, **file_data},
            follow=True,
        )

        feedback = Feedback.objects.last()

        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.text, form_data["text"])
        self.assertEqual(feedback.userinfo.mail, form_data["mail"])

    def test_feedback_upload_file(self):
        test_file = django.core.files.uploadedfile.SimpleUploadedFile(
            name="test_file2.txt",
            content=b"This is a test file content.",
            content_type="text/plain",
        )
        form_data = {
            "text": "This is a feedback text.",
            "mail": "test@example.com",
            "name": "Test User",
        }

        file_data = {"files": [test_file]}

        _ = self.client.post(
            django.urls.reverse("feedback:feedback"),
            data={**form_data, **file_data},
            follow=True,
        )
        feedback = Feedback.objects.last()

        feedback_file = FeedbackFile.objects.filter(feedback=feedback).first()
        self.assertIsNotNone(feedback_file)
        self.assertEqual(
            feedback_file.file.name,
            f"uploads/{feedback.id}/test_file2.txt",
        )
