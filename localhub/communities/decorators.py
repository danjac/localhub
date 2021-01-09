# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later
# Standard Library
import functools

# Django
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _


def community_required(allow_non_members=False,):
    def decorator(fn):
        @functools.wrap(fn)
        def wrapper(request, *args, **kwargs):
            if not request.community.active:
                return handle_community_not_found(request)

            if (
                not request.user.has_perm(
                    "communities.view_community", request.community
                )
                and not allow_non_members
                and not request.community.public
            ):
                return handle_community_access_denied(request)

            return fn(request, *args, **kwargs)

        return wrapper

    return decorator


def handle_community_access_denied(request):
    if request.is_ajax():
        raise PermissionDenied(_("You must be a member of this community"))
    return HttpResponseRedirect(reverse("community_welcome"))


def handle_community_not_found(request):
    if request.is_ajax():
        raise Http404(_("No community is available for this domain"))
    return HttpResponseRedirect(reverse("community_not_found"))
