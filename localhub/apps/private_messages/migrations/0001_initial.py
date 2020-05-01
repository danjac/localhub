# Generated by Django 3.0.5 on 2020-04-23 03:12

import django.contrib.postgres.search
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import model_utils.fields

import localhub.markdown.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("communities", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Message",
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
                ("message", localhub.markdown.fields.MarkdownField()),
                ("read", models.DateTimeField(blank=True, null=True)),
                ("recipient_deleted", models.DateTimeField(blank=True, null=True)),
                ("sender_deleted", models.DateTimeField(blank=True, null=True)),
                (
                    "search_document",
                    django.contrib.postgres.search.SearchVectorField(
                        editable=False, null=True
                    ),
                ),
                (
                    "community",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="communities.Community",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="replies",
                        to="private_messages.Message",
                    ),
                ),
            ],
        ),
    ]
