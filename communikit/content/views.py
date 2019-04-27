from typing import Dict, Any

from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.db.models import QuerySet
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.models import Community
from communikit.communities.views import CommunityRequiredMixin
from communikit.content.forms import PostForm
from communikit.content.models import Post


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


class PostListView(CommunityRequiredMixin, ListView):
    paginate_by = 12

    def get_queryset(self) -> QuerySet:
        return (
            Post.objects.filter(community=self.request.community)
            .order_by("-created")
            .select_related("author", "community")
            .select_subclasses()
        )

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data.update({"form": PostForm()})
        return data


post_list_view = PostListView.as_view()
