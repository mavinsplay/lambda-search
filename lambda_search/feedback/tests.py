from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

__all__ = []


class StaticURLTests(TestCase):
    def test_feedback_endpoint(self):
        response = Client().get(reverse("feedback:feedback"))
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f"error feedback endpoint, code: {response.status_code}",
        )
