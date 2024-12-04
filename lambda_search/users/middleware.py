from django.utils.deprecation import MiddlewareMixin

from users.models import User

__all__ = []


class ProxyUserMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.user = User.objects.get(pk=request.user.pk)

        return self.get_response(request)
