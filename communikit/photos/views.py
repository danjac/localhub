from communikit.activities.views import (
    ActivityCreateView,
    ActivityDeleteView,
    ActivityDetailView,
    ActivityDislikeView,
    ActivityLikeView,
    ActivityListView,
    ActivityUpdateView,
)
from communikit.notifications.views import NotificationMarkReadView
from communikit.photos.forms import PhotoForm
from communikit.posts.models import Photo, PhotoNotification


photo_create_view = ActivityCreateView.as_view(
    model=Photo, form_class=PhotoForm
)

photo_list_view = ActivityListView.as_view(
    model=Photo
)

photo_detail_view = ActivityDetailView.as_view(model=Photo)

photo_update_view = ActivityUpdateView.as_view(
    model=Photo, form_class=PhotoForm
)

photo_delete_view = ActivityDeleteView.as_view(
    model=Photo
)

photo_like_view = ActivityLikeView.as_view(model=Photo)

photo_dislike_view = ActivityDislikeView.as_view(model=Photo)

photo_notification_mark_read_view = NotificationMarkReadView.as_view(
    model=PhotoNotification
)
