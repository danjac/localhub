from django.utils.translation import ugettext_lazy as _

from communikit.activities.views import (
    BaseActivityCreateView,
    BaseActivityDeleteView,
    BaseActivityDetailView,
    BaseActivityDislikeView,
    BaseActivityLikeView,
    BaseActivityUpdateView,
)
from communikit.posts.forms import PostForm
from communikit.posts.models import Post


class PostCreateView(BaseActivityCreateView):
    model = Post
    form_class = PostForm


post_create_view = PostCreateView.as_view()


class PostDetailView(BaseActivityDetailView):
    select_subclass = "post"


post_detail_view = PostDetailView.as_view()


class PostUpdateView(BaseActivityUpdateView):
    select_subclass = "post"
    form_class = PostForm


post_update_view = PostUpdateView.as_view()


class PostDeleteView(BaseActivityDeleteView):
    select_subclass = "post"
    success_message = _("Your post has been deleted")


post_delete_view = PostDeleteView.as_view()


class PostLikeView(BaseActivityLikeView):
    select_subclass = "post"


post_like_view = PostLikeView.as_view()


class PostDislikeView(BaseActivityDislikeView):
    select_subclass = "post"


post_dislike_view = PostDislikeView.as_view()
