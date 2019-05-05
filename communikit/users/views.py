from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, DetailView, UpdateView
from django.views.generic.detail import SingleObjectMixin

from communikit.communities.views import CommunityRequiredMixin

User = get_user_model()


class CurrentUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(self) -> User:
        return self.request.user


class ProfileUserMixin(CommunityRequiredMixin, SingleObjectMixin):
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "profile"

    def get(self, request, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object(
            queryset=User.objects.filter(communities=request.community)
        )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        data["is_own_profile"] = (
            self.request.user.is_authenticated
            and self.request.user == self.object
        )
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
