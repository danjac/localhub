# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

# Localhub
from localhub.activities.urls.generic import create_activity_urls

# Local
from . import views
from .forms import PollForm
from .models import Poll

app_name = "polls"


urlpatterns = create_activity_urls(
    Poll,
    PollForm,
    detail_view=views.poll_detail_view,
    update_view=views.poll_update_view,
    create_view=views.poll_create_view,
    list_view=views.poll_list_view,
) + [path("<int:pk>~vote/", views.answer_vote_view, name="vote")]
