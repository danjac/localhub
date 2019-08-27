# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.db.models import Model
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic import (
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.activities.breadcrumbs import get_breadcrumbs_for_instance
from localhub.comments.forms import CommentForm
from localhub.comments.models import Comment
from localhub.comments.notifications import (
    send_comment_notifications,
    send_comment_deleted_email,
)
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.views import BreadcrumbsMixin, SearchMixin
from localhub.flags.forms import FlagForm
from localhub.likes.models import Like


class CommentQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return (
            Comment.objects.get_queryset()
            .for_community(self.request.community)
            .select_related("owner", "community")
        )


class MultipleCommentMixin(CommentQuerySetMixin, MultipleObjectMixin):
    ...


class SingleCommentMixin(CommentQuerySetMixin, SingleObjectMixin):
    ...


class CommentParentMixin:
    object: Model

    @cached_property
    def parent(self):
        return self.object.content_object

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["parent"] = self.parent
        return data


class SingleCommentView(SingleCommentMixin, View):
    ...


class CommentDetailView(
    CommentQuerySetMixin, CommentParentMixin, BreadcrumbsMixin, DetailView
):
    def get_breadcrumbs(self):
        if self.parent:
            return get_breadcrumbs_for_instance(self.parent) + [
                (self.request.path, _("Comment"))
            ]
        return []

    def get_flags(self):
        return (
            self.object.get_flags().select_related("user").order_by("-created")
        )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.community, self.request.user)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.user.has_perm(
            "communities.moderate_community", self.request.community
        ):
            data["flags"] = self.get_flags()
        return data


comment_detail_view = CommentDetailView.as_view()


class CommentUpdateView(
    PermissionRequiredMixin,
    CommentQuerySetMixin,
    CommentParentMixin,
    BreadcrumbsMixin,
    UpdateView,
):
    form_class = CommentForm
    permission_required = "comments.change_comment"

    def get_success_url(self):
        return self.parent.get_absolute_url()

    def get_breadcrumbs(self):
        if self.parent:
            return get_breadcrumbs_for_instance(self.parent) + [
                (self.request.path, _("Edit Comment"))
            ]
        return []

    def form_valid(self, form: ModelForm):
        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.save()
        for notification in self.object.notify_on_update():
            send_comment_notifications(self.object, notification)
        messages.success(self.request, _("Comment has been updated"))
        return HttpResponseRedirect(self.get_success_url())


comment_update_view = CommentUpdateView.as_view()


class CommentDeleteView(
    PermissionRequiredMixin,
    CommentQuerySetMixin,
    CommentParentMixin,
    DeleteView,
):
    permission_required = "comments.delete_comment"

    def get_success_url(self):
        return self.parent.get_absolute_url()

    def delete(self, request: HttpRequest, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        if self.request.user != self.object.owner:
            send_comment_deleted_email(self.object)

        messages.success(request, _("Comment has been deleted"))
        return HttpResponseRedirect(self.get_success_url())


comment_delete_view = CommentDeleteView.as_view()


class CommentLikeView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleCommentView
):
    permission_required = "comments.like_comment"

    def post(self, request: HttpRequest, *args, **kwargs):
        self.object = self.get_object()
        try:
            like = Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=self.object.owner,
                content_object=self.object,
            )
            for notification in like.notify():
                send_comment_notifications(self.object, notification)
        except IntegrityError:
            # dupe, ignore
            pass
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())


comment_like_view = CommentLikeView.as_view()


class CommentDislikeView(LoginRequiredMixin, SingleCommentView):
    def post(self, request: HttpRequest, *args, **kwargs):
        self.object = self.get_object()
        Like.objects.filter(user=request.user, comment=self.object).delete()
        if request.is_ajax():
            return HttpResponse(status=204)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def delete(self, request: HttpRequest, *args, **kwargs):
        return self.post(request, *args, **kwargs)


comment_dislike_view = CommentDislikeView.as_view()


class CommentFlagView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SingleCommentMixin,
    BreadcrumbsMixin,
    CommentParentMixin,
    FormView,
):
    form_class = FlagForm
    template_name = "flags/flag_form.html"
    permission_required = "comments.flag_comment"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_has_flagged(self.request.user)
            .exclude(has_flagged=True)
        )

    def get_permission_object(self):
        return self.object

    def get_breadcrumbs(self):
        return get_breadcrumbs_for_instance(self.parent) + [
            (self.request.path, _("Flag Comment"))
        ]

    def get_success_url(self):
        return self.parent.get_absolute_url()

    def form_valid(self, form):
        flag = form.save(commit=False)
        flag.content_object = self.object
        flag.community = self.request.community
        flag.user = self.request.user
        flag.save()

        for notification in flag.notify():
            send_comment_notifications(self.object, notification)
        messages.success(
            self.request, _("This comment has been flagged to the moderators")
        )
        return HttpResponseRedirect(self.get_success_url())


comment_flag_view = CommentFlagView.as_view()


class CommentListView(MultipleCommentMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE


class CommentSearchView(SearchMixin, CommentListView):
    template_name = "comments/search.html"

    def get_queryset(self):
        if not self.search_query:
            return self.none()
        return (
            super()
            .get_queryset()
            .blocked_users(self.request.user)
            .search(self.search_query)
            .order_by("rank")
        )


comment_search_view = CommentSearchView.as_view()
