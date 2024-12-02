from django.views.generic import TemplateView

__all__ = ()


class HomeView(TemplateView):
    template_name = "homepage/main.html"
