from communikit.activities.views import (
    ActivityCreateView,
    ActivityDeleteView,
    ActivityDetailView,
    ActivityDislikeView,
    ActivityLikeView,
    ActivityUpdateView,
)
from communikit.notifications.views import NotificationMarkReadView
from communikit.posts.forms import PostForm
from communikit.posts.models import Post, PostNotification


post_create_view = ActivityCreateView.as_view(model=Post, form_class=PostForm)

post_detail_view = ActivityDetailView.as_view(model=Post)

post_update_view = ActivityUpdateView.as_view(model=Post, form_class=PostForm)

post_delete_view = ActivityDeleteView.as_view(
    model=Post
)

post_like_view = ActivityLikeView.as_view(model=Post)

post_dislike_view = ActivityDislikeView.as_view(model=Post)

post_notification_mark_read_view = NotificationMarkReadView.as_view(
    model=PostNotification
)
