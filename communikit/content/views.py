from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.content.forms import PostForm
from communikit.content.models import Post
from communikit.intercooler.views import (
    IntercoolerCreateView,
    IntercoolerDeleteView,
    IntercoolerDetailView,
    IntercoolerListView,
    IntercoolerUpdateView,
)


class CommunityPostQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Post.objects.filter(
            community=self.request.community
        ).select_related("author", "community")


class PostCreateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    IntercoolerCreateView,
):

    model = Post
    form_class = PostForm
    permission_required = "content.create_post"
    success_url = reverse_lazy("content:list")
    ic_template_name = "content/includes/post_create.html"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_template_names(self) -> List[str]:
        if "cancel" in self.request.GET:
            return ["content/includes/post_share.html"]
        return super().get_template_names()

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        self.object.community = self.request.community
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


post_create_view = PostCreateView.as_view()


class PostListView(CommunityPostQuerySetMixin, IntercoolerListView):
    paginate_by = 12
    allow_empty = True
    ic_template_name = "content/includes/post_list.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("-created").select_subclasses()


post_list_view = PostListView.as_view()


class PostDetailView(CommunityPostQuerySetMixin, IntercoolerDetailView):
    ic_template_name = "content/includes/post_detail.html"

    def post(self, *args, **kwargs):
        return self.get(*args, **kwargs)


post_detail_view = PostDetailView.as_view()


class PostUpdateView(
    LoginRequiredMixin, CommunityPostQuerySetMixin, IntercoolerUpdateView
):
    form_class = PostForm
    permission_required = "content.change_post"
    ic_template_name = "content/includes/post_update.html"
    ic_success_template_name = "content/includes/post_detail.html"


post_update_view = PostUpdateView.as_view()


class PostDeleteView(
    LoginRequiredMixin,
    CommunityPostQuerySetMixin,
    PermissionRequiredMixin,
    IntercoolerDeleteView,
):
    permission_required = "content.delete_post"
    success_url = reverse_lazy("content:list")


post_delete_view = PostDeleteView.as_view()
