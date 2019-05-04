from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
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
from communikit.communities.views import CommunityRequiredMixin
from communikit.content.models import Post
from communikit.users.views import ProfileUserMixin


class CommunityCommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Comment.objects.filter(
            post__community=self.request.community
        ).select_related("author", "post", "post__community")


class CommentDetailView(CommunityCommentQuerySetMixin, DetailView):
    pass


comment_detail_view = CommentDetailView.as_view()


class CommentCreateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    form_class = CommentForm
    permission_required = "comments.create_comment"

    @cached_property
    def parent(self) -> Post:
        try:
            return Post.objects.get(
                community=self.request.community, pk=self.kwargs["pk"]
            )
        except Post.DoesNotExist:
            raise Http404

    def get_permission_object(self) -> Post:
        return self.parent

    def get_success_url(self):
        return self.parent.get_absolute_url()

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.post = self.parent
        self.object.author = self.request.user
        self.object.save()
        messages.success(self.request, _("Your comment has been posted"))
        return HttpResponseRedirect(self.get_success_url())


comment_create_view = CommentCreateView.as_view()


class CommentUpdateView(
    LoginRequiredMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    form_class = CommentForm
    permission_required = "comments.change_comment"

    def get_success_url(self) -> str:
        return self.object.post.get_absolute_url()


comment_update_view = CommentUpdateView.as_view()


class CommentDeleteView(
    LoginRequiredMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    permission_required = "comments.delete_comment"

    def get_success_url(self) -> str:
        return self.object.post.get_absolute_url()

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.get_success_url())


comment_delete_view = CommentDeleteView.as_view()


class ProfileCommentListView(ProfileUserMixin, ListView):
    template_name = "comments/profile_comment_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            Comment.objects.filter(
                author=self.profile, post__community=self.request.community
            )
            .select_related("author", "post", "post__community")
            .order_by("-created")
        )


profile_comment_list_view = ProfileCommentListView.as_view()
