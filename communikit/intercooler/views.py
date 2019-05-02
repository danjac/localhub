from typing import List

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.edit import ModelFormMixin


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

    If an ic_success_template_name  is provided will render to this class if
    Intercooler request target.

    IntercoolerRequestMiddleware must be enabled.
    """

    ic_success_template_name = None

    def get_ic_success_template_name(self) -> str:
        return self.ic_success_template_name

    def get_success_response(self, **kwargs) -> HttpResponse:
        ic_success_template_name = self.get_ic_success_template_name()
        if self.request.is_intercooler() and ic_success_template_name:
            return self.response_class(
                request=self.request,
                template=ic_success_template_name,
                context=self.get_context_data(object=self.object),
                using=self.template_engine,
                **kwargs,
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
        if request.is_intercooler() and request.intercooler_data.target_id:
            self.get_object().delete()
            response = HttpResponse()
            response["X-IC-Remove"] = self.delay
            return response
        return super().delete(request, *args, **kwargs)


class IntercoolerDeleteView(IntercoolerDeletionMixin, DeleteView):
    pass
