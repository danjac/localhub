# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

# Local
from ..views import generic


def create_activity_urls(
    model,
    form_class=None,
    *,
    bookmark_view=generic.activity_bookmark_view,
    create_comment_view=generic.create_comment_view,
    create_view=generic.activity_create_view,
    delete_view=generic.activity_delete_view,
    detail_view=generic.activity_detail_view,
    flag_view=generic.activity_flag_view,
    like_view=generic.activity_like_view,
    list_view=generic.activity_list_view,
    pin_view=generic.activity_pin_view,
    publish_view=generic.activity_publish_view,
    reshare_view=generic.activity_reshare_view,
    update_tags_view=generic.activity_update_tags_view,
    update_view=generic.activity_update_view,
):
    """
    Generates default URL patterns for activity subclasses.

    Simple usage (in a urls.py)

    urlpatterns = create_activity_urls(Post)
    """

    detail_template_name = resolve_template_names(model, "_detail")
    form_template_name = resolve_template_names(model, "_form")

    return [
        path(
            "",
            list_view,
            kwargs={
                "model": model,
                "template_name": resolve_template_names(model, "_list"),
            },
            name="list",
        ),
        path(
            "~create",
            create_view,
            name="create",
            kwargs={
                "model": model,
                "form_class": form_class,
                "template_name": form_template_name,
            },
        ),
        path(
            "~create-private",
            create_view,
            name="create_private",
            kwargs={
                "model": model,
                "form_class": form_class,
                "template_name": form_template_name,
                "is_private": True,
            },
        ),
        path(
            "<int:pk>/~comment/",
            create_comment_view,
            name="comment",
            kwargs={"model": model,},
        ),
        path("<int:pk>/~delete/", delete_view, name="delete", kwargs={"model": model},),
        path("<int:pk>/~like/", like_view, name="like", kwargs={"model": model,},),
        path(
            "<int:pk>/~dislike/",
            like_view,
            name="dislike",
            kwargs={"model": model, "remove": True,},
        ),
        path("<int:pk>/~flag/", flag_view, name="flag", kwargs={"model": model}),
        path("<int:pk>/~pin/", pin_view, name="pin", kwargs={"model": model,},),
        path(
            "<int:pk>/~unpin/",
            pin_view,
            name="unpin",
            kwargs={"model": model, "remove": True,},
        ),
        path(
            "<int:pk>/~reshare/",
            reshare_view,
            name="reshare",
            kwargs={"model": model,},
        ),
        path(
            "<int:pk>/~bookmark/",
            bookmark_view,
            name="bookmark",
            kwargs={"model": model,},
        ),
        path(
            "<int:pk>/~bookmark/remove/",
            bookmark_view,
            name="remove_bookmark",
            kwargs={"model": model, "remove": True,},
        ),
        path(
            "<int:pk>/~publish/",
            publish_view,
            name="publish",
            kwargs={"model": model,},
        ),
        path(
            "<int:pk>/~update/",
            update_view,
            name="update",
            kwargs={
                "model": model,
                "form_class": form_class,
                "template_name": form_template_name,
            },
        ),
        path(
            "<int:pk>/~update-tags/",
            update_tags_view,
            name="update_tags",
            kwargs={"model": model, "template_name": form_template_name,},
        ),
        path(
            "<int:pk>/<slug:slug>/",
            detail_view,
            name="detail",
            kwargs={"model": model, "template_name": detail_template_name,},
        ),
        path(
            "<int:pk>/",
            detail_view,
            name="detail_no_slug",
            kwargs={"model": model, "template_name": detail_template_name,},
        ),
    ]


def resolve_template_names(model, suffix):

    base_template_name = "/".join((model._meta.app_label, model._meta.model_name))

    return [
        f"{base_template_name}{suffix}.html",
        f"activities/activity{suffix}.html",
    ]
