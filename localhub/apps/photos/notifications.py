# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Localhub
# Social-BFG
from localhub.apps.activities.notifications import ActivityAdapter
from localhub.apps.notifications.decorators import register

# Local
from .models import Photo


@register(Photo)
class PhotoAdapter(ActivityAdapter):
    ...
