# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localhub.activities.notifications import ActivityAdapter
from localhub.notifications.decorators import register

from .models import Photo


@register(Photo)
class PhotoAdapter(ActivityAdapter):
    ...
