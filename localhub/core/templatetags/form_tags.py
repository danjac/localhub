# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django import template
from django.utils.translation import gettext_lazy as _


register = template.Library()


@register.inclusion_tag("includes/forms/ajax_form.html", takes_context=True)
def simple_ajax_form(
    context, form, multipart=False, action=None, submit_btn=_("Submit")
):
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
