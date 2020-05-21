# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import permissions


class IsCommunity(permissions.BasePermission):
    """Checks if current community present and active"""

    def has_permission(self, request, view):
        return request.community.active


class IsCommunityMember(permissions.BasePermission):
    """Checks if user has any active membership with
    current community.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_member(
            request.community
        )


class IsCommunityModerator(permissions.BasePermission):
    """Checks if user has moderator rights in current community.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator(
            request.community
        )


class IsCommunityAdmin(permissions.BasePermission):
    """Checks if user has admin rights in current community
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin(
            request.community
        )
