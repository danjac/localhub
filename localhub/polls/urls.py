# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from localhub.activities.views import create_activity_urls

from .forms import PollForm
from .models import Poll
from .views import (
    PollCreateView,
    PollDetailView,
    PollListView,
    PollUpdateView,
    answer_vote_view,
)

app_name = "polls"


urlpatterns = create_activity_urls(
    Poll,
    PollForm,
    create_view_class=PollCreateView,
    detail_view_class=PollDetailView,
    list_view_class=PollListView,
    update_view_class=PollUpdateView,
) + [path("<int:pk>~vote/", answer_vote_view, name="vote")]
