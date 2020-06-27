# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

# Localhub
from localhub.activities.views.streams import activity_stream_view
from localhub.communities.views import (
    community_list_view,
    community_not_found_view,
    community_welcome_view,
)
from localhub.users.views import dismiss_notice_view, user_delete_view, user_update_view

urlpatterns = [
    # Local
    path("", view=activity_stream_view, name="activity_stream"),
    path("", include("localhub.activities.urls")),
    path("bookmarks/", include("localhub.bookmarks.urls")),
    path("comments/", include("localhub.comments.urls")),
    path("events/", include("localhub.events.urls")),
    path("flags/", include("localhub.flags.urls")),
    path("invites/", include("localhub.invites.urls")),
    path("join-requests/", include("localhub.join_requests.urls")),
    path("notifications/", include("localhub.notifications.urls")),
    path("favorites/", include("localhub.likes.urls")),
    path("messages/", include("localhub.private_messages.urls")),
    path("photos/", include("localhub.photos.urls")),
    path("polls/", include("localhub.polls.urls")),
    path("posts/", include("localhub.posts.urls")),
    path("people/", include("localhub.users.urls")),
    path("community/", include("localhub.communities.urls")),
    path("tags/", include("localhub.hashtags.urls")),
    path("communities/", community_list_view, name="community_list"),
    path("account/~update", user_update_view, name="user_update"),
    path("account/~delete", user_delete_view, name="user_delete"),
    path("welcome/", view=community_welcome_view, name="community_welcome"),
    path("not-found/", view=community_not_found_view, name="community_not_found"),
    path("~dismiss-notice/<str:notice>/", dismiss_notice_view, name="dismiss_notice"),
    # Third-party
    path("account/", include("allauth.urls")),
    path("markdownx/", include("markdownx.urls")),
    path("grappelli/", include("grappelli.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]

if settings.DEBUG:

    if "silk" in settings.INSTALLED_APPS:
        urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

    # static views
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # allow preview/debugging of error views in development
    urlpatterns += [
        path("errors/400/", TemplateView.as_view(template_name="400.html")),
        path("errors/403/", TemplateView.as_view(template_name="403.html")),
        path("errors/404/", TemplateView.as_view(template_name="404.html")),
        path("errors/405/", TemplateView.as_view(template_name="405.html")),
        path("errors/500/", TemplateView.as_view(template_name="500.html")),
        path("errors/csrf/", TemplateView.as_view(template_name="403_csrf.html")),
    ]
