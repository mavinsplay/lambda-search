import re

from django.http import Http404


__all__ = ()


class ProtectedMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.protected_path = re.compile(r"^/media/protected/")

    def __call__(self, request):
        if self.protected_path.match(request.path):
            raise Http404("Доступ запрещен")

        return self.get_response(request)
