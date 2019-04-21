from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    # placeholder
    path("", RedirectView.as_view(url="/account/")),
    path("admin/", admin.site.urls),
    path("auth/", include("allauth.urls")),
    path("account/", include("communikit.users.urls")),
]

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls))
    ] + urlpatterns
