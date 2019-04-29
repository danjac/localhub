from typing import Dict, Any

from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.intercooler.views import (
    IntercoolerTemplateMixin,
    IntercoolerDeleteView,
)
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
        return HttpResponseRedirect(self.get_success_url())


post_create_view = PostCreateView.as_view()


class PostListView(
    CommunityPostQuerySetMixin, IntercoolerTemplateMixin, ListView
):
    paginate_by = 12
    allow_empty = True
    ic_template_name = "content/includes/post_list.html"

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("-created").select_subclasses()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "content.create_post", self.request.community
        ):
            data["form"] = PostForm()
        return data


post_list_view = PostListView.as_view()


class PostDetailView(CommunityPostQuerySetMixin, DetailView):
    pass


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
    IntercoolerDeleteView,
):
    permission_required = "content.delete_post"
    success_url = reverse_lazy("content:list")


post_delete_view = PostDeleteView.as_view()
