from django.utils.translation import ugettext_lazy as _

from communikit.activities.views import (
    BaseActivityCreateView,
    BaseActivityDeleteView,
    BaseActivityDetailView,
    BaseActivityUpdateView,
)
from communikit.posts.forms import PostForm
from communikit.posts.models import Post


class PostCreateView(BaseActivityCreateView):
    model = Post
    form_class = PostForm


post_create_view = PostCreateView.as_view()


class PostDetailView(BaseActivityDetailView):
    pass


post_detail_view = PostDetailView.as_view()


class PostUpdateView(BaseActivityUpdateView):
    form_class = PostForm


post_update_view = PostUpdateView.as_view()


class PostDeleteView(BaseActivityDeleteView):
    success_message = _("Your post has been deleted")


post_delete_view = PostDeleteView.as_view()
