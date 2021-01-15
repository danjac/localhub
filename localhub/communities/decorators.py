# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later
# Standard Library
import functools

# Django
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect
from django.utils.translation import gettext as _


def community_required(view=None, *, allow_non_members=False):
    if view is None:
        return functools.partial(
            community_required, allow_non_members=allow_non_members
        )

    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.community.active:
            if request.is_ajax():
                raise Http404(_("No community is available for this domain"))
            return redirect("community_not_found")
        if (
            not request.user.has_perm("communities.view_community", request.community)
            and not allow_non_members
            and not request.community.public
        ):
            if request.is_ajax():
                raise PermissionDenied(_("You must be a member of this community"))
            return redirect("community_welcome")

        return view(request, *args, **kwargs)

    return wrapper
