# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

# Local
from ..views import generic


def create_activity_urls(
    model,
    form_class=None,
    list_view=generic.activity_list_view,
    create_view_class=generic.ActivityCreateView,
    update_view_class=generic.ActivityUpdateView,
    detail_view_class=generic.ActivityDetailView,
    delete_view_class=generic.ActivityDeleteView,
    flag_view_class=generic.ActivityFlagView,
    like_view_class=generic.ActivityLikeView,
    dislike_view_class=generic.ActivityDislikeView,
    reshare_view_class=generic.ActivityReshareView,
    publish_view_class=generic.ActivityPublishView,
    pin_view_class=generic.ActivityPinView,
    unpin_view_class=generic.ActivityUnpinView,
    bookmark_view_class=generic.ActivityBookmarkView,
    remove_bookmark_view_class=generic.ActivityRemoveBookmarkView,
    update_tags_view_class=generic.ActivityUpdateTagsView,
    create_comment_view=generic.create_comment_view,
    list_view_class=None,
):
    """
    Generates default URL patterns for activity subclasses.

    Simple usage (in a urls.py)

    urlpatterns = create_activity_urls(Post)
    """

    base_template_name = "/".join((model._meta.app_label, model._meta.model_name))

    return [
        path(
            "",
            list_view,
            kwargs={"model": model, "template_name": base_template_name + "_list.html"},
            name="list",
        )
        if list_view
        else path(list_view_class.as_view(model=model), name="list"),
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
            create_comment_view,
            name="comment",
            kwargs={"model": model,},
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
