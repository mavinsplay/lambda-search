from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

__all__ = []


class StaticURLTests(TestCase):
    def test_about_endpoint(self):
        response = Client().get(reverse("about:about"))
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f"error about endpoint, code: {response.status_code}",
        )

    def test_terms_endpoint(self):
        response = Client().get(reverse("about:terms"))
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f"error about_terms endpoint, code: {response.status_code}",
        )
