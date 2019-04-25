from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView, UpdateView, DeleteView

User = get_user_model()


class CurrentUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(self) -> User:
        return self.request.user


class UserDetailView(CurrentUserMixin, DetailView):
    pass


user_detail_view = UserDetailView.as_view()


class UserUpdateView(CurrentUserMixin, SuccessMessageMixin, UpdateView):
    fields = ("name",)

    success_url = reverse_lazy("users:detail")
    success_message = _("Your details have been updated")


user_update_view = UserUpdateView.as_view()


class UserDeleteView(CurrentUserMixin, DeleteView):
    success_url = reverse_lazy("account_login")


user_delete_view = UserDeleteView.as_view()
