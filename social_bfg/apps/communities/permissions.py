# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import permissions


class IsCommunity(permissions.BasePermission):
    """Checks if current community present and active"""

    def has_permission(self, request, view):
        return (
            request.community.active
            and request.user.is_authenticated
            and request.user.is_active
            and self.has_community_permission(request, view)
        )

    def has_community_permission(self, request, view):
        return True


class IsCommunityMember(IsCommunity):
    """Checks if user has any active membership with
    current community.
    """

    def has_community_permission(self, request, view):
        return request.user.is_member(request.community)


class IsCommunityModerator(IsCommunity):
    """Checks if user has moderator rights in current community.
    """

    def has_community_permission(self, request, view):
        return request.user.is_moderator(request.community)


class IsCommunityAdmin(IsCommunity):
    """Checks if user has admin rights in current community
    """

    def has_community_permission(self, request, view):
        return request.user.is_admin(request.community)
