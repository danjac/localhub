from django.urls import path

from communikit.comments.views import (
    comment_create_view,
    comment_delete_view,
    comment_detail_view,
    comment_dislike_view,
    comment_like_view,
    comment_profile_view,
    comment_update_view,
)

app_name = "comments"


urlpatterns = [
    path("~create/<int:pk>/", comment_create_view, name="create"),
    path("comment/<int:pk>/", comment_detail_view, name="detail"),
    path("comment/<int:pk>/~update/", comment_update_view, name="update"),
    path("comment/<int:pk>/~delete/", comment_delete_view, name="delete"),
    path("comment/<int:pk>/~like/", comment_like_view, name="like"),
    path("comment/<int:pk>/~dislike/", comment_dislike_view, name="dislike"),
    path("profile/<username>/", comment_profile_view, name="profile"),
]
