# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
import django.dispatch

# should be sent when an individual notification is marked read
notification_read = django.dispatch.Signal(providing_args=["instance"])
