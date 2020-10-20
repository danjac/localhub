# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.core.management.base import BaseCommand, CommandError

# Localhub
from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Community


class Command(BaseCommand):
    help = "Creates fake users for testing purposes"

    def add_arguments(self, parser):
        parser.add_argument(
            "domain", help="Community domain e.g. mydomain.localhub.social"
        )
        parser.add_argument("num_users", help="Number of fake users", type=int)

    def handle(self, *args, **options):

        domain = options["domain"]
        num_users = options["num_users"]

        try:
            community = Community.objects.get(domain__iexact=domain)
        except Community.DoesNotExist:
            raise CommandError(f"No community found matching {domain}")

        MembershipFactory.create_batch(num_users, community=community)

        self.stdout.write(self.style.SUCCESS(f"{num_users} fake users created"))
