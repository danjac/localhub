# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from localhub.activities.views.detail import ActivityDetailView
from localhub.activities.views.list import ActivityListView

from .mixins import PollQuerySetMixin


class PollDetailView(PollQuerySetMixin, ActivityDetailView):
    ...


class PollListView(PollQuerySetMixin, ActivityListView):
    ...
