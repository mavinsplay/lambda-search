from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

__all__ = ()


class TermsView(TemplateView):
    template_name = "about/terms.html"

    def get_context_data(self, **kwargs) -> dict[str]:
        context = super().get_context_data(**kwargs)
        context["title"] = _("User Agreement")
        language_code = get_language()
        context["terms_file"] = f"includes/terms/terms_{language_code}.html"
        return context


class AboutView(TemplateView):
    template_name = "about/about.html"
