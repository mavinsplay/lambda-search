import django.contrib.auth
from django.utils.deprecation import MiddlewareMixin

from users.models import User

__all__ = []


class ProxyUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                User.create_profile(request.user)
                profile = User.objects.get_queryset()
                request.user = profile.get(pk=request.user.pk)
            except AttributeError:
                request.user = django.contrib.auth.get_user_model()
