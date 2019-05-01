from django.http import Http404
from django.contrib.auth.views import LoginRequiredMixin
from django.utils.functional import cached_property

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.views import CommunityRequiredMixin
from communikit.content.models import Post
from communikit.intercooler.views import (
    IntercoolerCreateView,
    IntercoolerUpdateView,
    IntercoolerDeleteView,
    IntercoolerDetailView,
)
from communikit.comments.models import Comment


class CommunityCommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Comment.objects.filter(
            post__community=self.request.community
        ).select_related("author", "post", "post__community")


class CommentDetailView(CommunityCommentQuerySetMixin, IntercoolerDetailView):
    ic_template_name = "comments/includes/comment_detail.html"


comment_detail_view = CommentDetailView.as_view()


class CommentFormMixin:
    ic_template_name = "comments/includes/comment_form.html"
    detail_view = CommentDetailView.as_view()


class CommentCreateView(
    LoginRequiredMixin,
    CommentFormMixin,
    PermissionRequiredMixin,
    IntercoolerCreateView,
):
    permission_required = "comments:create_comment"

    @cached_property
    def parent(self):
        try:
            return Post.objects.get(
                community=self.request.community, pk=self.kwargs["pk"]
            )
        except Post.DoesNotExist:
            raise Http404

    def get_permission_object(self):
        return self.parent

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.post = self.parent
        self.object.author = self.request.user
        self.object.save()
        return self.get_success_response()


class CommentUpdateView(
    LoginRequiredMixin,
    CommentFormMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    IntercoolerUpdateView,
):
    permission_required = "comments:change_comment"


comment_update_view = CommentUpdateView.as_view()


class CommunityDeleteView(
    LoginRequiredMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    IntercoolerDeleteView,
):
    permission_required = "comments:delete_comment"
