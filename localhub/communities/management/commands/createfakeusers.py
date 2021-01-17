# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import getpass

# Django
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError

# Localhub
from localhub.communities.factories import MembershipFactory
from localhub.communities.models import Community


class Command(BaseCommand):
    help = "Creates fake users for a community"

    def add_arguments(self, parser):
        parser.add_argument(
            "domain", help="Community domain e.g. mydomain.localhub.social"
        )

        parser.add_argument(
            "num_users",
            help="Number of fake users",
            type=int,
        )

    def handle(self, *args, **options):

        num_users = options["num_users"]
        domain = options["domain"]

        try:
            community = Community.objects.get(domain__iexact=domain)
        except Community.DoesNotExist:
            raise CommandError(f"No community found for {domain}")

        if (
            input(
                f"This will create {num_users} new users for community {community.name}. Do you wish to continue ? (Y/n) "
            ).lower()
            != "y"
        ):
            return

        password = getpass.getpass(
            "Password (leave empty for randomized password): "
        ).strip()

        num_created = 0

        for _ in range(num_users):
            try:
                membership = MembershipFactory(community=community)
                if password:
                    membership.member.set_password(password)
                    membership.member.save()
                num_created += 1
                self.stdout.write(
                    " | ".join((membership.member.username, membership.member.email))
                )
            except IntegrityError:
                ...

        self.stdout.write(self.style.SUCCESS(f"{num_created} new users created"))
