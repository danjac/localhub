from django.db.models import Count, QuerySet
from django.utils.translation import ugettext_lazy as _

from communikit.activities.views import (
    BaseActivityCreateView,
    BaseActivityDeleteView,
    BaseActivityDetailView,
    BaseActivityUpdateView,
)
from communikit.communities.views import CommunityRequiredMixin
from communikit.posts.forms import PostForm
from communikit.posts.models import Post


class CommunityPostQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Post.objects.filter(
            community=self.request.community
        ).select_related("owner", "community")


class PostCreateView(BaseActivityCreateView):
    model = Post
    form_class = PostForm


post_create_view = PostCreateView.as_view()


class PostDetailView(CommunityPostQuerySetMixin, BaseActivityDetailView):
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(num_likes=Count("likes"), num_comments=Count("comment"))
        )


post_detail_view = PostDetailView.as_view()


class PostUpdateView(CommunityPostQuerySetMixin, BaseActivityUpdateView):
    form_class = PostForm


post_update_view = PostUpdateView.as_view()


class PostDeleteView(CommunityPostQuerySetMixin, BaseActivityDeleteView):
    success_message = _("Your post has been deleted")


post_delete_view = PostDeleteView.as_view()
