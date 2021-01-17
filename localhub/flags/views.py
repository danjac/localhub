# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

# Third Party Libraries
from turbo_response import redirect_303, render_form_response

# Localhub
from localhub.common.forms import process_form
from localhub.communities.decorators import community_moderator_required

# Local
from .forms import FlagForm
from .models import Flag


@community_moderator_required
@login_required
def flag_list_view(request):
    flags = (
        Flag.objects.filter(community=request.community)
        .select_related("user")
        .prefetch_related("content_object")
        .order_by("-created")
    )
    return TemplateResponse(request, "flags/flag_list.html", {"flags": flags})


@community_moderator_required
@login_required
def flag_delete_view(request, pk):
    flag = get_object_or_404(Flag.objects.filter(community=request.community), pk=pk)
    flag.delete()
    return redirect(flag.content_object.get_absolute_url())


def handle_flag_create(request, model):
    with process_form(request, FlagForm) as (form, success):
        if success:
            flag = form.save(commit=False)
            flag.content_object = model
            flag.community = request.community
            flag.user = request.user
            flag.save()

            flag.notify()

            success_message = _("This %(model)s has been flagged to the moderators") % {
                "model": model._meta.verbose_name
            }
            messages.success(request, success_message)
            return redirect_303(model)

        return render_form_response(
            request, form, "flags/flag_form.html", context={"parent": model}
        )
