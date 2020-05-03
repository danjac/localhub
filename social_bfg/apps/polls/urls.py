# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

# Social-BFG
from social_bfg.apps.activities.urls.generic import create_activity_urls

from . import views
from .forms import PollForm
from .models import Poll

app_name = "polls"


urlpatterns = create_activity_urls(
    Poll,
    PollForm,
    create_view_class=views.PollCreateView,
    detail_view_class=views.PollDetailView,
    list_view_class=views.PollListView,
    update_view_class=views.PollUpdateView,
) + [path("<int:pk>~vote/", views.answer_vote_view, name="vote")]
