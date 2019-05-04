from typing import Dict, Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Prefetch, QuerySet
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from rules.contrib.views import PermissionRequiredMixin

from communikit.comments.forms import CommentForm
from communikit.comments.models import Comment
from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.content.forms import PostForm
from communikit.content.models import Post


class CommunityPostQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
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


class PostListView(CommunityPostQuerySetMixin, ListView):
    paginate_by = 12
    allow_empty = True

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(num_comments=Count("comment"))
            .order_by("-created")
            .select_subclasses()
        )


post_list_view = PostListView.as_view()


class ProfilePostListView(PostListView):
    template_name = "content/profile_post_list.html"

    def get(self, request, username, *args, **kwargs) -> HttpResponse:
        self.profile = self.get_profile()
        return super().get(request, *args, **kwargs)

    def get_profile(self) -> settings.AUTH_USER_MODEL:
        try:
            return (
                get_user_model()
                ._default_manager.filter(communities=self.request.community)
                .get(username=self.kwargs["username"])
            )
        except ObjectDoesNotExist:
            raise Http404

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(author=self.profile)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        print(self.get_template_names())
        data = super().get_context_data(**kwargs)
        data["profile"] = self.profile
        return data


profile_post_list_view = ProfilePostListView.as_view()


class PostDetailView(CommunityPostQuerySetMixin, DetailView):
    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .annotate(num_comments=Count("comment"))
            .prefetch_related(
                Prefetch(
                    "comment_set",
                    to_attr="comments",
                    queryset=Comment.objects.select_related(
                        "author", "post", "post__community"
                    ).order_by("created"),
                )
            )
            .order_by("-created")
            .select_subclasses()
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm("comments:create"):
            data["comment_form"] = CommentForm()
        return data


post_detail_view = PostDetailView.as_view()


class PostUpdateView(
    LoginRequiredMixin, CommunityPostQuerySetMixin, UpdateView
):
    form_class = PostForm
    permission_required = "content.change_post"


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
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.get_success_url())


post_delete_view = PostDeleteView.as_view()
