# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponseRedirect

from localhub.views import SuccessDeleteView, SuccessGenericModelView

from .mixins import NotificationQuerySetMixin, NotificationSuccessRedirectMixin


class NotificationDeleteAllView(
    NotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessGenericModelView
):
    def delete(self, request):
        self.get_queryset().delete()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request):
        return self.delete(request)


notification_delete_all_view = NotificationDeleteAllView.as_view()


class NotificationDeleteView(
    NotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessDeleteView
):

    ...


notification_delete_view = NotificationDeleteView.as_view()
