from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.generic import DeleteView, DetailView, FormView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.activities.models import Activity
from communikit.comments.forms import CommentForm
from communikit.comments.models import Comment
from communikit.communities.views import CommunityRequiredMixin
from communikit.types import ContextDict


class SingleCommentMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Comment.objects.filter(
            activity__community=self.request.community
        ).select_related("owner", "activity", "activity__community")

    def get_parent(self) -> Activity:
        return Activity.objects.select_related(
            "community", "owner"
        ).get_subclass(pk=self.object.activity_id)

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["parent"] = self.get_parent()
        return data


class CommentCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CommunityRequiredMixin,
    SingleObjectMixin,
    FormView,
):
    form_class = CommentForm
    template_name = "comments/comment_form.html"
    permission_required = "comments.create_comment"

    def dispatch(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet:
        return Activity.objects.filter(
            community=self.request.community
        ).select_subclasses()

    def get_permission_object(self) -> Activity:
        return self.object

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def form_valid(self, form) -> HttpResponse:
        comment = form.save(commit=False)
        comment.activity = self.object
        comment.owner = self.request.user
        comment.save()
        messages.success(self.request, _("Your comment has been posted"))
        return HttpResponseRedirect(self.get_success_url())


comment_create_view = CommentCreateView.as_view()


class CommentDetailView(SingleCommentMixin, DetailView):
    pass


comment_detail_view = CommentDetailView.as_view()


class CommentUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleCommentMixin, UpdateView
):
    form_class = CommentForm
    permission_required = "comments.change_comment"

    def get_success_url(self) -> str:
        return self.get_parent().get_absolute_url()


comment_update_view = CommentUpdateView.as_view()


class CommentDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleCommentMixin, DeleteView
):
    permission_required = "comments.delete_comment"

    def get_success_url(self) -> str:
        return self.get_parent().get_absolute_url()

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, _("Your comment has been deleted"))
        return HttpResponseRedirect(self.get_success_url())


comment_delete_view = CommentDeleteView.as_view()
