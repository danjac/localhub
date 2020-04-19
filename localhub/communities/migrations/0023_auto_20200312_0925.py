# Generated by Django 3.0.4 on 2020-03-12 09:25

import django.core.validators
from django.db import migrations, models

import sorl.thumbnail.fields

import localhub.markdown.fields


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0022_auto_20200312_0915"),
    ]

    operations = [
        migrations.AlterField(
            model_name="community",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="allow_join_requests",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="blacklisted_email_addresses",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="blacklisted_email_domains",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="content_warning_tags",
            field=models.TextField(blank=True, default="#nsfw"),
        ),
        migrations.AlterField(
            model_name="community",
            name="description",
            field=localhub.markdown.fields.MarkdownField(blank=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="email_domain",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="This is not a valid domain",
                        regex="([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*\\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\\.?|localhost)",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="community",
            name="intro",
            field=localhub.markdown.fields.MarkdownField(blank=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="logo",
            field=sorl.thumbnail.fields.ImageField(
                blank=True, null=True, upload_to="logo"
            ),
        ),
        migrations.AlterField(
            model_name="community",
            name="public",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="community", name="tagline", field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="community",
            name="terms",
            field=localhub.markdown.fields.MarkdownField(blank=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="active",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="allow_join_requests",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="blacklisted_email_addresses",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="blacklisted_email_domains",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="content_warning_tags",
            field=models.TextField(blank=True, default="#nsfw"),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="description",
            field=localhub.markdown.fields.MarkdownField(blank=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="email_domain",
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="This is not a valid domain",
                        regex="([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*\\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\\.?|localhost)",
                    )
                ],
            ),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="intro",
            field=localhub.markdown.fields.MarkdownField(blank=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="logo",
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="public",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="tagline",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="historicalcommunity",
            name="terms",
            field=localhub.markdown.fields.MarkdownField(blank=True),
        ),
    ]
