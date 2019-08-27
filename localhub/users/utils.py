# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


def user_display(user):
    """
    Returns default rendering of a user. Used with the
    django_allauth user_display template tag.
    """
    return user.name or user.username
