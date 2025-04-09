from django.http import Http404

__all__ = ()


class ProtectedMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/media/protected/"):
            raise Http404("Доступ запрещен")

        return self.get_response(request)
