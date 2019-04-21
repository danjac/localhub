from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, DeleteView

User = get_user_model()


class CurrentUserMixin:
    def get_object(self) -> User:
        return self.request.user


class UserDetailView(LoginRequiredMixin, CurrentUserMixin, DetailView):
    # TBD: we also want read-only profile view at some point of other
    # users, but need to work out permissions, visibility rules etc.
    pass


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, CurrentUserMixin, UpdateView):
    fields = ("username", "name")

    success_url = reverse_lazy("users:detail")


user_update_view = UserUpdateView.as_view()


class UserDeleteView(LoginRequiredMixin, CurrentUserMixin, DeleteView):
    success_url = reverse_lazy("account_login")


user_delete_view = UserDeleteView.as_view()
