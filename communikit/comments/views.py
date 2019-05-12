from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin

from notifications.signals import notify

from rules.contrib.views import PermissionRequiredMixin

from communikit.comments.forms import CommentForm
from communikit.comments.models import Comment
from communikit.communities.views import CommunityRequiredMixin
from communikit.content.models import Post
from communikit.content.views import CommunityPostQuerySetMixin
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
    PermissionRequiredMixin,
    CommunityPostQuerySetMixin,
    SingleObjectMixin,
    FormView,
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "comments.create_comment"

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self) -> Post:
        return self.object

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def notify(self, comment: Comment):

        if comment.post.author != self.request.user:
            notify.send(
                self.request.user,
                recipient=comment.post.author,
                verb="comment_created",
                action_object=self.object,
                target=self.request.community,
            )
        mentions = comment.extract_mentions()

        if mentions:
            notify.send(
                self.request.user,
                recipient=self.request.community.members.exclude(
                    pk=self.request.user.pk
                ).filter(username__in=mentions),
                verb="comment_mentioned",
                action_object=comment,
                target=self.request.community,
            )

    def form_valid(self, form) -> HttpResponse:
        comment = form.save(commit=False)
        comment.post = self.object
        comment.author = self.request.user
        comment.save()
        self.notify(comment)
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
        messages.success(request, _("Your comment has been deleted"))
        return HttpResponseRedirect(self.get_success_url())


comment_delete_view = CommentDeleteView.as_view()


class ProfileCommentListView(ProfileUserMixin, ListView):
    template_name = "comments/profile_comment_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            Comment.objects.filter(
                author=self.object, post__community=self.request.community
            )
            .annotate(num_likes=Count("likes"))
            .select_related("author", "post", "post__community")
            .order_by("-created")
        )


profile_comment_list_view = ProfileCommentListView.as_view()


class CommentLikeView(
    LoginRequiredMixin,
    CommunityCommentQuerySetMixin,
    PermissionRequiredMixin,
    SingleObjectMixin,
    View,
):
    permission_required = "comments.like_comment"

    def post(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        is_liked = self.object.like(request.user)
        if is_liked:
            notify.send(
                request.user,
                recipient=self.object.author,
                verb="comment_liked",
                action_object=self.object,
                target=request.community,
            )
        if request.is_ajax():
            return HttpResponse(_("Unlike") if is_liked else _("Like"))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


comment_like_view = CommentLikeView.as_view()
