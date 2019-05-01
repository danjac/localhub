from django.contrib.auth.views import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import Http404, HttpResponse
from django.utils.functional import cached_property

from rules.contrib.views import PermissionRequiredMixin

from communikit.comments.models import Comment
from communikit.communities.views import CommunityRequiredMixin
from communikit.content.models import Post
from communikit.intercooler.views import (
    IntercoolerCreateView,
    IntercoolerDeleteView,
    IntercoolerDetailView,
    IntercoolerUpdateView,
)


class CommunityCommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Comment.objects.filter(
            post__community=self.request.community
        ).select_related("author", "post", "post__community")


class CommentDetailView(CommunityCommentQuerySetMixin, IntercoolerDetailView):
    ic_template_name = "comments/includes/comment_detail.html"


comment_detail_view = CommentDetailView.as_view()


class CommentIntercoolerFormMixin:
    ic_template_name = "comments/includes/comment_form.html"
    detail_view = CommentDetailView


class CommentCreateView(
    LoginRequiredMixin,
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    CommentIntercoolerFormMixin,
    IntercoolerCreateView,
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
        return self.get_success_response()


comment_create_view = CommentCreateView.as_view()


class CommentUpdateView(
    LoginRequiredMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    CommentIntercoolerFormMixin,
    IntercoolerUpdateView,
):
    permission_required = "comments:change_comment"


comment_update_view = CommentUpdateView.as_view()


class CommentDeleteView(
    LoginRequiredMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    IntercoolerDeleteView,
):
    permission_required = "comments:delete_comment"


comment_delete_view = CommentDeleteView.as_view()
