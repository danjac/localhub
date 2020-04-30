# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.views.generic import DetailView

from .mixins import InviteRecipientQuerySetMixin


class InviteDetailView(InviteRecipientQuerySetMixin, DetailView):
    ...


invite_detail_view = InviteDetailView.as_view()
