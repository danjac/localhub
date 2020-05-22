# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# Social-BFG
from social_bfg.apps.activities.views.streams import activity_stream_view
from social_bfg.apps.communities.views import (
    community_list_view,
    community_not_found_view,
    community_welcome_view,
)
from social_bfg.apps.events.api import EventViewSet
from social_bfg.apps.photos.api import PhotoViewSet
from social_bfg.apps.polls.api import PollViewSet
from social_bfg.apps.posts.api import PostViewSet
from social_bfg.apps.users.views import (
    dismiss_notice_view,
    user_delete_view,
    user_update_view,
)
from social_bfg.views.frontend import frontend_view

router = DefaultRouter()

router.register("posts", PostViewSet, basename="posts")
router.register("events", EventViewSet, basename="events")
router.register("photos", PhotoViewSet, basename="photos")
router.register("polls", PollViewSet, basename="polls")


urlpatterns = [
    path("", view=activity_stream_view, name="activity_stream"),
    path("", include("social_bfg.apps.activities.urls")),
    # TBD: merge stream URLs into single include
    path("api/", include(router.urls)),
    path("spa/", frontend_view),
    path("bookmarks/", include("social_bfg.apps.bookmarks.urls")),
    path("comments/", include("social_bfg.apps.comments.urls")),
    path("events/", include("social_bfg.apps.events.urls")),
    path("flags/", include("social_bfg.apps.flags.urls")),
    path("invites/", include("social_bfg.apps.invites.urls")),
    path("join-requests/", include("social_bfg.apps.join_requests.urls")),
    path("notifications/", include("social_bfg.apps.notifications.urls")),
    path("favorites/", include("social_bfg.apps.likes.urls")),
    path("messages/", include("social_bfg.apps.private_messages.urls")),
    path("photos/", include("social_bfg.apps.photos.urls")),
    path("polls/", include("social_bfg.apps.polls.urls")),
    path("posts/", include("social_bfg.apps.posts.urls")),
    path("people/", include("social_bfg.apps.users.urls")),
    path("community/", include("social_bfg.apps.communities.urls")),
    path("tags/", include("social_bfg.apps.hashtags.urls")),
    path("communities/", community_list_view, name="community_list"),
    path("account/~update", user_update_view, name="user_update"),
    path("account/~delete", user_delete_view, name="user_delete"),
    path("welcome/", view=community_welcome_view, name="community_welcome"),
    path("not-found/", view=community_not_found_view, name="community_not_found"),
    path("~dismiss-notice/<str:notice>/", dismiss_notice_view, name="dismiss_notice"),
    # Third-party
    path("account/", include("allauth.urls")),
    path("markdownx/", include("markdownx.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]

# silk
if "silk" in settings.INSTALLED_APPS:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

if settings.DEBUG:

    # debug toolbar
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

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
