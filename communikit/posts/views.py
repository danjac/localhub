from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from rules.contrib.views import PermissionRequiredMixin

from communikit.comments.forms import CommentForm
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.content.forms import PostForm
from communikit.content.models import Post
from communikit.types import ContextDict


class CommunityPostQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Post.objects.filter(
            community=self.request.community
        ).select_related("author", "community")


class PostCreateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):

    model = Post
    form_class = PostForm
    permission_required = "content.create_post"
    success_url = reverse_lazy("content:list")

    def get_permission_object(self) -> Community:
        return self.request.community

    def form_valid(self, form) -> HttpResponse:

        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.community = self.request.community
        self.object.save()

        messages.success(self.request, _("Your update has been posted"))
        return HttpResponseRedirect(self.get_success_url())


post_create_view = PostCreateView.as_view()


class PostDetailView(CommunityPostQuerySetMixin, DetailView):
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
    form_class = PostForm
    permission_required = "content.change_post"
    success_message = _("Your post has been saved")


post_update_view = PostUpdateView.as_view()


class PostDeleteView(
    LoginRequiredMixin,
    CommunityPostQuerySetMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    permission_required = "content.delete_post"
    success_url = reverse_lazy("content:list")

    def delete(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()

        messages.success(self.request, _("Your post has been deleted"))

        return HttpResponseRedirect(self.get_success_url())


post_delete_view = PostDeleteView.as_view()
