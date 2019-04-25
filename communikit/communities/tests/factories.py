from factory import DjangoModelFactory, Faker, Sequence

from communikit.communities.models import Community


class CommunityFactory(DjangoModelFactory):
    name = Faker("company")
    description = Faker("text")
    domain = Sequence(lambda n: "%d.example.com" % n)

    class Meta:
        model = Community
