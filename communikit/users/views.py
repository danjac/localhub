# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from communikit.communities.views import CommunityRequiredMixin


class CurrentUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(self) -> settings.AUTH_USER_MODEL:
        return self.request.user


class UserProfileMixin(CommunityRequiredMixin, SingleObjectMixin):
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile"

    def get(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object(
            queryset=get_user_model().objects.filter(
                communities=request.community
            )
        )
        return super().get(request, *args, **kwargs)


class UserDetailView(CurrentUserMixin, DetailView):
    pass


user_detail_view = UserDetailView.as_view()


class UserUpdateView(CurrentUserMixin, SuccessMessageMixin, UpdateView):
    fields = ("name",)

    success_url = reverse_lazy("users:update")
    success_message = _("Your details have been updated")


user_update_view = UserUpdateView.as_view()


class UserDeleteView(CurrentUserMixin, DeleteView):
    success_url = reverse_lazy("account_login")


user_delete_view = UserDeleteView.as_view()
