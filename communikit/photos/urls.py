# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from communikit.photos.views import (
    photo_create_view,
    photo_delete_view,
    photo_detail_view,
    photo_dislike_view,
    photo_like_view,
    photo_list_view,
    photo_update_view,
)

app_name = "photos"

urlpatterns = [
    path("", photo_list_view, name="list"),
    path("~create", photo_create_view, name="create"),
    path("<int:pk>/~update/", photo_update_view, name="update"),
    path("<int:pk>/~delete/", photo_delete_view, name="delete"),
    path("<int:pk>/~like/", photo_like_view, name="like"),
    path("<int:pk>/~dislike/", photo_dislike_view, name="dislike"),
    path("<int:pk>/<slug:slug>/", photo_detail_view, name="detail"),
]
