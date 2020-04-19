# Generated by Django 3.0.5 on 2020-04-19 14:36

from django.db import migrations

import localhub.users.fields


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0025_auto_20200419_1419"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalphoto",
            name="mentions",
            field=localhub.users.fields.MentionsField(blank=True, max_length=300),
        ),
        migrations.AlterField(
            model_name="photo",
            name="mentions",
            field=localhub.users.fields.MentionsField(blank=True, max_length=300),
        ),
    ]
