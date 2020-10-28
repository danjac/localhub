# Generated by Django 3.0.5 on 2020-04-23 03:12

# Django
import django.contrib.postgres.search
import django.utils.timezone
from django.db import migrations, models

# Third Party Libraries
import django_countries.fields
import model_utils.fields
import timezone_field.fields

# Localhub
import localhub.common.markdown.fields
import localhub.hashtags.fields
import localhub.users.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Event",
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
                ("title", models.CharField(max_length=300)),
                (
                    "hashtags",
                    localhub.hashtags.fields.HashtagsField(blank=True, max_length=300),
                ),
                (
                    "mentions",
                    localhub.users.fields.MentionsField(blank=True, max_length=300),
                ),
                (
                    "description",
                    localhub.common.markdown.fields.MarkdownField(blank=True),
                ),
                ("allow_comments", models.BooleanField(default=True)),
                ("is_reshare", models.BooleanField(default=False)),
                ("is_pinned", models.BooleanField(default=False)),
                ("edited", models.DateTimeField(blank=True, null=True)),
                ("published", models.DateTimeField(blank=True, null=True)),
                ("deleted", models.DateTimeField(blank=True, null=True)),
                (
                    "search_document",
                    django.contrib.postgres.search.SearchVectorField(
                        editable=False, null=True
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        blank=True, max_length=500, null=True, verbose_name="Link"
                    ),
                ),
                ("starts", models.DateTimeField(verbose_name="Starts on (UTC)")),
                ("ends", models.DateTimeField(blank=True, null=True)),
                ("timezone", timezone_field.fields.TimeZoneField(default="UTC")),
                ("canceled", models.DateTimeField(blank=True, null=True)),
                ("venue", models.CharField(blank=True, max_length=200)),
                ("ticket_price", models.CharField(blank=True, max_length=200)),
                (
                    "ticket_vendor",
                    models.TextField(blank=True, verbose_name="Tickets available from"),
                ),
                ("contact_name", models.CharField(blank=True, max_length=200)),
                ("contact_phone", models.CharField(blank=True, max_length=30)),
                ("contact_email", models.EmailField(blank=True, max_length=254)),
                ("street_address", models.CharField(blank=True, max_length=200)),
                (
                    "locality",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="City or town"
                    ),
                ),
                ("postal_code", models.CharField(blank=True, max_length=20)),
                ("region", models.CharField(blank=True, max_length=200)),
                (
                    "country",
                    django_countries.fields.CountryField(
                        blank=True, max_length=2, null=True
                    ),
                ),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
            ],
            options={"abstract": False,},
        ),
    ]
