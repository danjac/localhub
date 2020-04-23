# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from ..views.actions import (
    ActivityBookmarkView,
    ActivityDislikeView,
    ActivityLikeView,
    ActivityPinView,
    ActivityPublishView,
    ActivityRemoveBookmarkView,
    ActivityReshareView,
    ActivityUnpinView,
)
from ..views.create_update import (
    ActivityCommentCreateView,
    ActivityCreateView,
    ActivityFlagView,
    ActivityUpdateTagsView,
    ActivityUpdateView,
)
from ..views.delete import ActivityDeleteView
from ..views.detail import ActivityDetailView
from ..views.list import ActivityListView


def create_activity_urls(
    model,
    form_class=None,
    list_view_class=ActivityListView,
    create_view_class=ActivityCreateView,
    update_view_class=ActivityUpdateView,
    detail_view_class=ActivityDetailView,
    delete_view_class=ActivityDeleteView,
    flag_view_class=ActivityFlagView,
    like_view_class=ActivityLikeView,
    dislike_view_class=ActivityDislikeView,
    reshare_view_class=ActivityReshareView,
    publish_view_class=ActivityPublishView,
    pin_view_class=ActivityPinView,
    unpin_view_class=ActivityUnpinView,
    bookmark_view_class=ActivityBookmarkView,
    remove_bookmark_view_class=ActivityRemoveBookmarkView,
    update_tags_view_class=ActivityUpdateTagsView,
    create_comment_view_class=ActivityCommentCreateView,
):
    """
    Generates default URL patterns for activity subclasses.

    Simple usage (in a urls.py)

    urlpatterns = create_activity_urls(Post)
    """
    return [
        path("", list_view_class.as_view(model=model), name="list"),
        path(
            "~create",
            create_view_class.as_view(model=model, form_class=form_class),
            name="create",
        ),
        path(
            "~create-private",
            create_view_class.as_view(
                model=model, form_class=form_class, is_private=True
            ),
            name="create_private",
        ),
        path(
            "<int:pk>/~comment/",
            create_comment_view_class.as_view(model=model),
            name="comment",
        ),
        path(
            "<int:pk>/~delete/", delete_view_class.as_view(model=model), name="delete",
        ),
        path(
            "<int:pk>/~dislike/",
            dislike_view_class.as_view(model=model),
            name="dislike",
        ),
        path("<int:pk>/~flag/", flag_view_class.as_view(model=model), name="flag",),
        path("<int:pk>/~like/", like_view_class.as_view(model=model), name="like",),
        path("<int:pk>/~pin/", pin_view_class.as_view(model=model), name="pin",),
        path("<int:pk>/~unpin/", unpin_view_class.as_view(model=model), name="unpin",),
        path(
            "<int:pk>/~reshare/",
            reshare_view_class.as_view(model=model),
            name="reshare",
        ),
        path(
            "<int:pk>/~bookmark/",
            bookmark_view_class.as_view(model=model),
            name="bookmark",
        ),
        path(
            "<int:pk>/~bookmark/remove/",
            remove_bookmark_view_class.as_view(model=model),
            name="remove_bookmark",
        ),
        path(
            "<int:pk>/~publish/",
            publish_view_class.as_view(model=model),
            name="publish",
        ),
        path(
            "<int:pk>/~update/",
            update_view_class.as_view(model=model, form_class=form_class),
            name="update",
        ),
        path(
            "<int:pk>/~update-tags/",
            update_tags_view_class.as_view(model=model),
            name="update_tags",
        ),
        path(
            "<int:pk>/<slug:slug>/",
            detail_view_class.as_view(model=model),
            name="detail",
        ),
        path(
            "<int:pk>/", detail_view_class.as_view(model=model), name="detail_no_slug",
        ),
    ]
