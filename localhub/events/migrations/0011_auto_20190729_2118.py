# Generated by Django 2.2.2 on 2019-07-29 21:18

from django.db import migrations

import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0010_auto_20190727_0918"),
    ]

    operations = [
        migrations.AlterField(
            model_name="event",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
