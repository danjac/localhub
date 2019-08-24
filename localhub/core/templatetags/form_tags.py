from typing import Optional

from django import template
from django.forms import Form
from django.utils.translation import gettext_lazy as _

from localhub.core.types import ContextDict

register = template.Library()


@register.inclusion_tag("includes/forms/ajax_form.html", takes_context=True)
def simple_ajax_form(
    context: ContextDict,
    form: Form,
    multipart: bool = False,
    action: Optional[str] = None,
    submit_btn: str = _("Submit"),
) -> ContextDict:
    """
    Renders a simple AJAX form including Stimulus bindings.
    """
    action = action or context["request"].path
    return {
        "action": action,
        "form": form,
        "multipart": multipart,
        "submit_btn": submit_btn,
    }
