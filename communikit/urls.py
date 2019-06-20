# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from communikit.communities.views import (
    community_access_denied_view,
    community_not_found_view,
)

urlpatterns = [
    # Local
    path("", include("communikit.activities.urls")),
    path("comments/", include("communikit.comments.urls")),
    path("events/", include("communikit.events.urls")),
    path("invites/", include("communikit.invites.urls")),
    path("join-requests/", include("communikit.join_requests.urls")),
    path("notifications/", include("communikit.notifications.urls")),
    path("photos/", include("communikit.photos.urls")),
    path("posts/", include("communikit.posts.urls")),
    path("settings/", include("communikit.communities.urls")),
    path("users/", include("communikit.users.urls")),
    path(
        "access-denied/",
        view=community_access_denied_view,
        name="community_access_denied",
    ),
    path(
        "not-found/", view=community_not_found_view, name="community_not_found"
    ),
    # Third-party
    path("account/", include("allauth.urls")),
    path("markdownx/", include("markdownx.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:

    # debug toolbar
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns

    # static views
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

    # allow preview/debugging of error views in development
    urlpatterns += [
        path("errors/400/", TemplateView.as_view(template_name="400.html")),
        path("errors/403/", TemplateView.as_view(template_name="403.html")),
        path("errors/404/", TemplateView.as_view(template_name="404.html")),
        path("errors/500/", TemplateView.as_view(template_name="500.html")),
    ]
