from django.utils.functional import cached_property


class SearchMixin:
    search_query_parameter = "q"

    @cached_property
    def search_query(self):
        return self.request.GET.get(self.search_query_parameter, "")
