from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

__all__ = []


class StaticURLTests(TestCase):
    def test_homepage_endpoint(self):
        response = Client().get(reverse("homepage:homepage"))
        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
            f"error home endpoint, code: {response.status_code}",
        )
