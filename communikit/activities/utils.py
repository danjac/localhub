# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional, Type

from urllib.parse import urlparse

from django.forms import ModelForm
from django.urls import URLPattern, path

from communikit.activities import views
from communikit.activities.models import Activity
from communikit.core.types import ViewType


def get_domain(url: str) -> Optional[str]:
    """
    Returns the domain of a URL. Removes any "www." at the start.
    Returns None if invalid.
    """
    if not url:
        return None
    domain = urlparse(url).netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def create_activity_urls(
    model: Type[Activity],
    form_class: Optional[Type[ModelForm]] = None,
    list_view_class: ViewType = views.ActivityListView,
    create_view_class: ViewType = views.ActivityCreateView,
    create_comment_view_class: ViewType = views.ActivityCommentCreateView,
    delete_view_class: ViewType = views.ActivityDeleteView,
    dislike_view_class: ViewType = views.ActivityDislikeView,
    flag_view_class: ViewType = views.ActivityFlagView,
    like_view_class: ViewType = views.ActivityLikeView,
    update_view_class: ViewType = views.ActivityUpdateView,
    detail_view_class: ViewType = views.ActivityDetailView,
) -> List[URLPattern]:
    """
    Generates default URL patterns for activity subclasses.

    Simple usage (in a urls.py)

    urlpatterns = create_activity_urls(Post)
    # add more urlpatterns...
    """
    return [
        path("", list_view_class.as_view(model=model), name="list"),
        path(
            "~create",
            create_view_class.as_view(model=model, form_class=form_class),
            name="create",
        ),
        path(
            "<int:pk>/~comment/",
            create_comment_view_class.as_view(model=model),
            name="comment",
        ),
        path(
            "<int:pk>/~delete/",
            delete_view_class.as_view(model=model),
            name="delete",
        ),
        path(
            "<int:pk>/~dislike/",
            dislike_view_class.as_view(model=model),
            name="dislike",
        ),
        path(
            "<int:pk>/~flag/",
            flag_view_class.as_view(model=model),
            name="flag",
        ),
        path(
            "<int:pk>/~like/",
            like_view_class.as_view(model=model),
            name="like",
        ),
        path(
            "<int:pk>/~update/",
            update_view_class.as_view(model=model, form_class=form_class),
            name="update",
        ),
        path(
            "<int:pk>/<slug:slug>/",
            detail_view_class.as_view(model=model),
            name="detail",
        ),
    ]
