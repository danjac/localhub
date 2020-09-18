# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Third Party Libraries
from factory import Faker, Sequence, SubFactory
from factory.django import DjangoModelFactory

# Localhub
from localhub.users.factories import UserFactory

# Local
from .models import Community, Membership


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
