import notifications.urls

from django.conf import settings
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Local
    path("", include("communikit.content.urls")),
    path("comments/", include("communikit.comments.urls")),
    path("settings/", include("communikit.communities.urls")),
    path("invites/", include("communikit.invites.urls")),
    path("users/", include("communikit.users.urls")),
    # Third-party
    path("account/", include("allauth.urls")),
    path("markdownx/", include("markdownx.urls")),
    path(
        "notifications/",
        include(notifications.urls, namespace="notifications"),
    ),
    path("admin/", admin.site.urls),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns
