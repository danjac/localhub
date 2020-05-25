# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

# Django Rest Framework
from rest_framework.routers import DefaultRouter

# Social-BFG
from social_bfg.apps.events.api import EventViewSet
from social_bfg.apps.photos.api import PhotoViewSet
from social_bfg.apps.polls.api import PollViewSet
from social_bfg.apps.posts.api import PostViewSet
from social_bfg.views.frontend import frontend_view

router = DefaultRouter()

router.register("posts", PostViewSet, basename="posts")
router.register("events", EventViewSet, basename="events")
router.register("photos", PhotoViewSet, basename="photos")
router.register("polls", PollViewSet, basename="polls")


urlpatterns = [
    path("api/streams/", include("social_bfg.apps.activities.urls")),
    # TBD: merge stream URLs into single include
    path("api/", include(router.urls)),
    # Third-party
    path("account/", include("allauth.urls")),
    path("markdownx/", include("markdownx.urls")),
    path(settings.ADMIN_URL, admin.site.urls),
]

if settings.DEBUG:

    # debug toolbar
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns

    # static views
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r"^.*", frontend_view),
]
