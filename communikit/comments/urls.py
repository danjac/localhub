from django.urls import path

from communikit.comments.views import (
    comment_create_view,
    comment_delete_view,
    comment_detail_view,
    comment_like_view,
    comment_update_view,
    profile_comment_list_view,
)

app_name = "comments"


urlpatterns = [
    path("~create/<int:pk>/", comment_create_view, name="create"),
    path("profile/<username>/", profile_comment_list_view, name="profile"),
    path("comment/<int:pk>/", comment_detail_view, name="detail"),
    path("comment/<int:pk>/~update/", comment_update_view, name="update"),
    path("comment/<int:pk>/~delete/", comment_delete_view, name="delete"),
    path("comment/<int:pk>/~like/", comment_like_view, name="like"),
]
