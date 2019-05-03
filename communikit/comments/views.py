from django.contrib.auth.views import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import Http404, HttpResponse
from django.utils.functional import cached_property
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from rules.contrib.views import PermissionRequiredMixin

from communikit.comments.forms import CommentForm
from communikit.comments.models import Comment
from communikit.communities.views import CommunityRequiredMixin
from communikit.content.models import Post


class CommunityCommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Comment.objects.filter(
            post__community=self.request.community
        ).select_related("author", "post", "post__community")


class CommentDetailView(CommunityCommentQuerySetMixin, DetailView):
    pass


comment_detail_view = CommentDetailView.as_view()


class CommentIntercoolerFormMixin:
    form_class = CommentForm
    ic_template_name = "comments/includes/comment_form.html"
    detail_view = CommentDetailView


class CommentCreateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    CommentIntercoolerFormMixin,
    CreateView,
):
    permission_required = "comments:create_comment"

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

    def form_valid(self, form) -> HttpResponse:
        self.object = form.save(commit=False)
        self.object.post = self.parent
        self.object.author = self.request.user
        self.object.save()


comment_create_view = CommentCreateView.as_view()


class CommentUpdateView(
    LoginRequiredMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    CommentIntercoolerFormMixin,
    UpdateView,
):
    permission_required = "comments:change_comment"


comment_update_view = CommentUpdateView.as_view()


class CommentDeleteView(
    LoginRequiredMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    permission_required = "comments:delete_comment"


comment_delete_view = CommentDeleteView.as_view()
