from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities.views import (
    BaseActivityCreateView,
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


class PostDeleteView(
    LoginRequiredMixin,
    CommunityPostQuerySetMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    # TBD: make a base activity delete view
    permission_required = "activities.delete_activity"
    success_url = reverse_lazy("activities:stream")

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        messages.success(self.request, _("Your post has been deleted"))

        return HttpResponseRedirect(self.get_success_url())


post_delete_view = PostDeleteView.as_view()
