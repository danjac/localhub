from typing import Any, Dict

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, DetailView, UpdateView
from django.views.generic.base import ContextMixin

from communikit.communities.views import CommunityRequiredMixin

User = get_user_model()


class CurrentUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(self) -> User:
        return self.request.user


class ProfileUserMixin(CommunityRequiredMixin, ContextMixin):
    @cached_property
    def profile(self) -> User:
        try:
            return User.objects.filter(communities=self.request.community).get(
                username=self.kwargs["username"]
            )
        except User.DoesNotExist:
            raise Http404

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        data = super().get_context_data(**kwargs)
        data["profile"] = self.profile
        return data


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
