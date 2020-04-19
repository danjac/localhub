# Generated by Django 2.2 on 2019-05-30 09:22

from typing import Any, List

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import model_utils.fields

import localhub.communities.models
import localhub.markdown.fields


class Migration(migrations.Migration):

    initial = True

    dependencies: List[Any] = []

    operations = [
        migrations.CreateModel(
            name="Community",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "domain",
                    models.CharField(
                        max_length=100,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="This is not a valid domain",
                                regex="([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*\\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\\.?|localhost)",
                            )
                        ],
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", localhub.markdown.fields.MarkdownField(blank=True),),
                (
                    "public",
                    models.BooleanField(
                        default=True,
                        help_text="This community is open to the world. Non-members can view all published content.",
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, help_text="This community is currently live.",
                    ),
                ),
            ],
            options={"verbose_name_plural": "Communities"},
        ),
        migrations.CreateModel(
            name="Membership",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("member", "Member"),
                            ("moderator", "Moderator"),
                            ("admin", "Admin"),
                        ],
                        db_index=True,
                        default="member",
                        max_length=9,
                    ),
                ),
                ("active", models.BooleanField(default=True)),
                (
                    "community",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="communities.Community",
                    ),
                ),
            ],
        ),
    ]
