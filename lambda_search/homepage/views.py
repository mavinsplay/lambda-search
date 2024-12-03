from django.views.generic import TemplateView

__all__ = ()


class HomeView(TemplateView):
    template_name = "homepage/main.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lambda Search"
        return context
