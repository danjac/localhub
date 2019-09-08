# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localhub.activities.views import create_activity_urls
from localhub.polls.forms import PollForm
from localhub.polls.models import Poll
from localhub.polls.views import PollCreateView, PollUpdateView

app_name = "polls"


urlpatterns = create_activity_urls(
    Poll,
    PollForm,
    create_view_class=PollCreateView,
    update_view_class=PollUpdateView,
)
