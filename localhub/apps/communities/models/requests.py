# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from dataclasses import dataclass

from django.http import HttpRequest


@dataclass
class RequestCommunity:
    """
    This works in a similar way to Django auth AnonymousUser, if
    no community present. It provides ducktyping so we don't have to check
    for None everywhere. Wraps HttpRequest/Site.
    """

    request: HttpRequest

    name: str
    domain: str

    id = None
    pk = None

    active: bool = False

    def get_absolute_url(self):
        return self.request.full_path

    def user_has_role(self, user, *roles):
        return False

    def is_member(self, user):
        return False

    def is_moderator(self, user):
        return False

    def is_admin(self, user):
        return False
