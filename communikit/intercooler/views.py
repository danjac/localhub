from typing import List, Optional

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import (
    ModelFormMixin,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    ListView,
    View,
)


class IntercoolerTemplateMixin:
    """
    If Intercooler header is present then uses ic_template_name
    instead of usual template.

    IntercoolerRequestMiddleware must be enabled.
    """

    ic_template_name = None

    def get_template_names(self) -> List[str]:
        if self.request.is_intercooler():
            if self.ic_template_name is None:
                raise ImproperlyConfigured("ic_template_name must be defined")
            return [self.ic_template_name]
        return super().get_template_names()


class IntercoolerDetailView(IntercoolerTemplateMixin, DetailView):
    pass


class IntercoolerDetailView(IntercoolerTemplateMixin, ListView):
    pass


class IntercoolerModelFormMixin(IntercoolerTemplateMixin, ModelFormMixin):
    """
    Provides a get_success_response on successful form completion.
    """

    detail_view = None

    def get_detail_view(self) -> Optional[View]:

        if self.detail_view:
            return self.detail_view.as_view()
        return None

    def get_success_response(self) -> HttpResponse:
        if self.request.is_intercooler() and self.intercooler_data.target_id:
            detail_view = self.get_detail_view()
            if detail_view:
                return detail_view.render_to_response(
                    context=detail_view.get_context_data(object=self.object)
                )
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save()
        return self.get_success_response()


class IntercoolerCreateView(IntercoolerModelFormMixin, CreateView):
    pass


class IntercoolerUpdateView(IntercoolerModelFormMixin, UpdateView):
    pass


class IntercoolerDeletionMixin:
    """
    If Intercooler request and target id will pass back the X-IC-Remove
    header

    IntercoolerRequestMiddleware must be enabled.
    """

    removal_delay = "500ms"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.is_intercooler() and request.intercooler_data.target_id:
            self.get_object().delete()
            response = HttpResponse()
            response["X-IC-Remove"] = self.removal_delay
            return response
        return super().delete(request, *args, **kwargs)


class IntercoolerDeleteView(IntercoolerDeletionMixin, DeleteView):
    pass
