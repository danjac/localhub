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
    model = Post


post_detail_view = PostDetailView.as_view()


class PostUpdateView(BaseActivityUpdateView):
    model = Post
    form_class = PostForm


post_update_view = PostUpdateView.as_view()


class PostDeleteView(BaseActivityDeleteView):
    model = Post
    success_message = _("Your post has been deleted")


post_delete_view = PostDeleteView.as_view()


class PostLikeView(BaseActivityLikeView):
    model = Post


post_like_view = PostLikeView.as_view()


class PostDislikeView(BaseActivityDislikeView):
    model = Post


post_dislike_view = PostDislikeView.as_view()
