# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from factory import DjangoModelFactory, Faker, Sequence, SubFactory

from localhub.communities.models import Community, Membership
from localhub.users.tests.factories import UserFactory


class CommunityFactory(DjangoModelFactory):
    name = Faker("company")
    description = Faker("text")
    domain = Sequence(lambda n: "%d.example.com" % n)

    class Meta:
        model = Community


class MembershipFactory(DjangoModelFactory):
    member = SubFactory(UserFactory)
    community = SubFactory(CommunityFactory)

    class Meta:
        model = Membership
