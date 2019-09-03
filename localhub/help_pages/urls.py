from django.urls import path

from localhub.help_pages.views import index_view, page_view

app_name = "help_pages"

urlpatterns = [
    path("", index_view, name="index"),
    path("<slug:page>/", page_view, name="page"),
]
