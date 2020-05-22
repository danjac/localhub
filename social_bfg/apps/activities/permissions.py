# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django Rest Framework
from rest_framework import permissions


class IsActivityOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user == obj.owner


class IsNotActivityOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner != request.user


class IsCommentAllowed(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.allow_comments


class IsPublished(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.published is not None
