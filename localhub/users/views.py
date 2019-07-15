# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from typing import Optional, Type

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.activities.models import Activity
from localhub.activities.views import BaseActivityStreamView
from localhub.comments.models import Comment
from localhub.comments.views import CommentListView
from localhub.communities.models import Community
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.types import ContextDict
from localhub.likes.models import Like
from localhub.subscriptions.models import Subscription


class AuthenticatedUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(
        self, queryset: Optional[QuerySet] = None
    ) -> settings.AUTH_USER_MODEL:
        return self.request.user


class UserUpdateView(AuthenticatedUserMixin, SuccessMessageMixin, UpdateView):
    fields = ("name", "avatar", "bio")

    success_message = _("Your details have been updated")

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()


user_update_view = UserUpdateView.as_view()


class UserDeleteView(AuthenticatedUserMixin, DeleteView):
    success_url = settings.HOME_PAGE_URL


user_delete_view = UserDeleteView.as_view()


class UserSlugMixin:
    slug_field = "username"


class UserContextMixin(ContextMixin):
    context_object_name = "user_obj"

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["is_auth_user"] = self.request.user == self.object
        return data


class UserQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return get_user_model().objects.active(self.request.community)


class UserDetailView(
    UserSlugMixin, UserContextMixin, UserQuerySetMixin, DetailView
):
    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        if (
            self.request.user.is_authenticated
            and self.object != self.request.user
        ):
            data["is_subscribed"] = Subscription.objects.filter(
                user=self.object, subscriber=self.request.user
            ).exists()
        return data


user_detail_view = UserDetailView.as_view()


class SingleUserView(
    UserSlugMixin, UserQuerySetMixin, SingleObjectMixin, View
):
    ...


class UserSubscribeView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleUserView
):
    permission_required = "subscriptions.create_subscription"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().exclude(pk=self.request.user.id)

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        Subscription.objects.create(
            subscriber=self.request.user,
            content_object=self.object,
            community=self.request.community,
        )

        messages.success(self.request, _("You are now following this user"))
        return HttpResponseRedirect(self.get_success_url())


user_subscribe_view = UserSubscribeView.as_view()


class UserUnsubscribeView(LoginRequiredMixin, SingleUserView):
    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        Subscription.objects.filter(
            object_id=self.object.id,
            content_type=ContentType.objects.get_for_model(self.object),
            subscriber=self.request.user,
        ).delete()
        messages.success(
            self.request, _("You have stopped following this user")
        )
        return HttpResponseRedirect(self.get_success_url())


user_unsubscribe_view = UserUnsubscribeView.as_view()


class BaseUserListView(UserQuerySetMixin, ListView):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("name", "username")


class UserListView(BaseUserListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self) -> QuerySet:

        qs = super().get_queryset()
        if self.request.user.is_authenticated:
            qs = qs.with_has_subscribed(
                self.request.user, self.request.community
            )
        return qs


user_list_view = UserListView.as_view()


class UserAutocompleteListView(BaseUserListView):
    template_name = "users/user_autocomplete_list.html"

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        search_term = self.request.GET.get("q", "").strip()
        if search_term:
            return qs.filter(
                Q(
                    Q(username__icontains=search_term)
                    | Q(name__icontains=search_term)
                )
            )
        return qs.none()


user_autocomplete_list_view = UserAutocompleteListView.as_view()


class SingleUserMixin(
    CommunityRequiredMixin, UserSlugMixin, UserContextMixin, SingleObjectMixin
):
    """
    Used to mix with views using non-user querysets
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object(
            queryset=get_user_model().objects.active(self.request.community)
        )
        return super().get(request, *args, **kwargs)


class UserActivityStreamView(SingleUserMixin, BaseActivityStreamView):

    active_tab = "posts"
    template_name = "users/activities.html"

    def get_queryset_for_model(self, model: Type[Activity]) -> QuerySet:
        return super().get_queryset_for_model(model).filter(owner=self.object)

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(*self.models)
            .filter(recipient=self.object, community=self.request.community)
            .count()
        )
        return data


user_activity_stream_view = UserActivityStreamView.as_view()


class UserCommentListView(SingleUserMixin, CommentListView):
    active_tab = "comments"
    template_name = "users/comments.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(owner=self.object)
            .with_common_annotations(self.request.community, self.request.user)
            .order_by("-created")
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(Comment)
            .filter(recipient=self.object, community=self.request.community)
            .count()
        )
        return data


user_comment_list_view = UserCommentListView.as_view()
