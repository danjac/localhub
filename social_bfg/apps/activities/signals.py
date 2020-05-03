# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
import django.dispatch

# should be sent when an activity is soft deleted by moderator.
soft_delete = django.dispatch.Signal(providing_args=["instance"])
