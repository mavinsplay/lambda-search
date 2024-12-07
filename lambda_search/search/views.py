from django.utils.translation import gettext as _
from django.views.generic.edit import FormView

from search.forms import SearchForm

__all__ = ()


class SearchView(FormView):  # TODO
    template_name = "search/search.html"
    form_class = SearchForm

    def form_valid(self, form):
        query = form.cleaned_data["search_query"]
        return self.render_to_response(self.get_context_data(results=query))

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(
                results=None,
                errors=form.errors,
            ),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = _("Search")
        return context
