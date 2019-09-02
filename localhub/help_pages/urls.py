from django.urls import path

from vanilla import TemplateView

app_name = "help_pages"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="help_pages/index.html"),
        name="index",
    ),
    path(
        "communities/",
        TemplateView.as_view(template_name="help_pages/communities.html"),
        name="communities",
    ),
]
