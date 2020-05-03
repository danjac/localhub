# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

# Social-BFG
from social_bfg.apps.communities.models import Community, Membership


class Command(BaseCommand):
    help = "Creates a new community"

    def add_arguments(self, parser):
        parser.add_argument(
            "domain", help="Community domain e.g. mydomain.social_bfg.social"
        )
        parser.add_argument("name", help="Full name of the community")
        parser.add_argument("--admin", default=None, help="Username of admin user")

    def handle(self, *args, **options):

        if Community.objects.filter(domain__iexact=options["domain"]).exists():
            raise CommandError("A community already exists for this domain")

        if options["admin"]:
            try:
                admin = get_user_model().objects.get(username=options["admin"])
            except ObjectDoesNotExist:
                raise CommandError("No user found matching this username")
        else:
            admin = None

        community = Community.objects.create(
            name=options["name"], domain=options["domain"], active=True
        )
        self.stdout.write(
            self.style.SUCCESS("Community '%s' has been created" % community.name)
        )
        if admin:
            Membership.objects.create(
                community=community, member=admin, role=Membership.Role.ADMIN
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "User '%s' has been added as community admin" % admin.username
                )
            )
