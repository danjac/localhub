# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from bfg.apps.activities.notifications import ActivityAdapter
from bfg.apps.notifications.decorators import register

from .models import Post


@register(Post)
class PostAdapter(ActivityAdapter):
    ...
