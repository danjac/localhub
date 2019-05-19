from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, DetailView, UpdateView

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities.views import BaseActivityCreateView
from communikit.comments.forms import CommentForm
from communikit.communities.views import CommunityRequiredMixin
from communikit.posts.forms import PostForm
from communikit.posts.models import Post
from communikit.types import ContextDict


class CommunityPostQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return (
            Post.objects.annotate(
                num_likes=Count("likes"), num_comments=Count("comment")
            )
            .filter(community=self.request.community)
            .select_related("author", "community")
        )


class PostCreateView(BaseActivityCreateView):
    model = Post
    form_class = PostForm


post_create_view = PostCreateView.as_view()


class PostDetailView(CommunityPostQuerySetMixin, DetailView):
    # TBD: make a base activity detail view
    def get_comments(self) -> QuerySet:
        return (
            self.object.comment_set.select_related(
                "author", "post", "post__community"
            )
            .annotate(num_likes=Count("likes"))
            .order_by("created"),
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["comments"] = self.get_comments()
        if self.request.user.has_perm("comments.create_comment", self.object):
            data["comment_form"] = CommentForm()
        return data


post_detail_view = PostDetailView.as_view()


class PostUpdateView(
    LoginRequiredMixin,
    SuccessMessageMixin,
    CommunityPostQuerySetMixin,
    UpdateView,
):
    # TBD: make a base activity update view
    form_class = PostForm
    permission_required = "activities.change_activity"
    success_message = _("Your post has been saved")


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
