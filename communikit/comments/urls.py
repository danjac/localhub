from django.urls import path

from communikit.comments.views import (
    comment_create_view,
    comment_delete_view,
    comment_detail_view,
    comment_dislike_view,
    comment_flag_view,
    comment_like_view,
    comment_update_view,
)

app_name = "comments"


urlpatterns = [
    path("~create/<int:pk>/", comment_create_view, name="create"),
    path("<int:pk>/", comment_detail_view, name="detail"),
    path("<int:pk>/~update/", comment_update_view, name="update"),
    path("<int:pk>/~delete/", comment_delete_view, name="delete"),
    path("<int:pk>/~like/", comment_like_view, name="like"),
    path("<int:pk>/~dislike/", comment_dislike_view, name="dislike"),
    path("<int:pk>/~flag/", comment_flag_view, name="flag"),
]
