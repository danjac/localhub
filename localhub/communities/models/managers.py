# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.apps import apps
from django.contrib.sites.shortcuts import get_current_site
from django.db import models

from localhub.common.db.search.mixins import SearchQuerySetMixin

from .requests import RequestCommunity


class MembershipQuerySet(SearchQuerySetMixin, models.QuerySet):
    search_document_field = "member__search_document"


class MembershipManager(models.Manager.from_queryset(MembershipQuerySet)):
    ...


class CommunityQuerySet(models.QuerySet):
    def with_num_members(self):
        return self.annotate(num_members=models.Count("membership"))

    def with_is_member(self, user):
        if user.is_authenticated:
            return self.annotate(
                is_member=models.Exists(
                    self.model.objects.filter(
                        membership__member=user,
                        membership__active=True,
                        membership__community=models.OuterRef("pk"),
                    )
                ),
                member_role=models.Subquery(
                    apps.get_model("communities.Membership")
                    .objects.filter(
                        member=user, active=True, community=models.OuterRef("pk"),
                    )
                    .values("role")[:1],
                ),
            )
        return self.annotate(
            is_member=models.Value(False, output_field=models.BooleanField()),
            member_role=models.Value(None, output_field=models.CharField()),
        )

    def accessible(self, user):
        """
        Returns all communities either listed publicly or where user is a member

        Args:
            user (User)

        Returns:
            QuerySet
        """
        return (
            self.with_is_member(user)
            .filter(models.Q(models.Q(is_member=True) | models.Q(public=True)))
            .distinct()
        )


class CommunityManager(models.Manager.from_queryset(CommunityQuerySet)):
    def get_current(self, request):
        """
        Returns current community matching request domain if active.
        """
        try:
            return self.get(active=True, domain__iexact=request.get_host())
        except self.model.DoesNotExist:
            site = get_current_site(request)
            return RequestCommunity(request, site.name, site.domain)
