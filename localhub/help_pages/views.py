from django.http import Http404
from django.template import TemplateDoesNotExist
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from vanilla import TemplateView


class IndexView(TemplateView):
    template_name = "help_pages/index.html"


index_view = IndexView.as_view()


class PageView(TemplateView):
    """
    Will try to render help page using pattern
    `help_pages/pages/{page}.html`.

    If template not found raises a 404.
    """

    def get_template_names(self):
        return [
            "help_pages/pages/%s.html" % self.kwargs["page"].replace("-", "_")
        ]

    def render_to_response(self, context):
        """
        Enforce resolution of template before it hits the common middleware, so
        we can catch the TemplateDoesNotExist error.
        """
        try:
            response = super().render_to_response(context)
            response.resolve_template(self.get_template_names())
            return response
        except TemplateDoesNotExist:
            raise Http404(_("This help page does not exist"))


page_view = PageView.as_view()
