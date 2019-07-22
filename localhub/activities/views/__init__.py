# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import List, Optional, Type

from django.forms import ModelForm
from django.urls import URLPattern, path

from localhub.activities.types import ActivityType
from localhub.core.types import ViewType

from . import generic


def create_activity_urls(
    model: ActivityType,
    form_class: Optional[Type[ModelForm]] = None,
    list_view_class: ViewType = generic.ActivityListView,
    create_view_class: ViewType = generic.ActivityCreateView,
    update_view_class: ViewType = generic.ActivityUpdateView,
    detail_view_class: ViewType = generic.ActivityDetailView,
    delete_view_class: ViewType = generic.ActivityDeleteView,
    dislike_view_class: ViewType = generic.ActivityDislikeView,
    flag_view_class: ViewType = generic.ActivityFlagView,
    like_view_class: ViewType = generic.ActivityLikeView,
    create_comment_view_class: ViewType = generic.ActivityCommentCreateView,
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
