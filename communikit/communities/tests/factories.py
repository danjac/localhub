from django.contrib.sites.models import Site

from factory import DjangoModelFactory, Faker, Sequence, SubFactory

from communikit.communities.models import Community


class SiteFactory(DjangoModelFactory):
    name = Faker("name")
    domain = Sequence(lambda n: "%d.example.com" % n)

    class Meta:
        model = Site


class CommunityFactory(DjangoModelFactory):
    name = Faker("company")
    description = Faker("text")
    site = SubFactory(SiteFactory)

    class Meta:
        model = Community
