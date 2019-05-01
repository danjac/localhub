from typing import List, Optional

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
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
    If Intercooler header is present then will try to
    return ic_template_name if available.

    IntercoolerRequestMiddleware must be enabled.
    """

    ic_template_name = None

    def get_ic_template_name(self) -> str:
        return self.ic_template_name

    def get_template_names(self) -> List[str]:
        if self.request.is_intercooler():
            ic_template_name = self.get_ic_template_name()
            if ic_template_name:
                return [ic_template_name]
        return super().get_template_names()


class IntercoolerDetailView(IntercoolerTemplateMixin, DetailView):
    pass


class IntercoolerListView(IntercoolerTemplateMixin, ListView):
    pass


class IntercoolerModelFormMixin(IntercoolerTemplateMixin, ModelFormMixin):
    """
    Provides a get_success_response on successful form completion.

    If a detail_view class is provided will render to this class if
    Intercooler request target.

    IntercoolerRequestMiddleware must be enabled.
    """

    detail_view = None

    def get_detail_view(self) -> Optional[View]:
        if self.detail_view:
            return self.detail_view.as_view()
        return None

    def get_success_response(self) -> HttpResponse:
        if self.request.is_intercooler_target():
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

    delay = "500ms"

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if request.is_intercooler_target():
            self.get_object().delete()
            response = HttpResponse()
            response["X-IC-Remove"] = self.delay
            return response
        return super().delete(request, *args, **kwargs)


class IntercoolerDeleteView(IntercoolerDeletionMixin, DeleteView):
    pass
