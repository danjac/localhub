# Generated by Django 3.0.5 on 2020-04-22 18:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0024_auto_20200419_1436"),
    ]

    operations = [
        migrations.RenameField(
            model_name="historicalpost",
            old_name="additional_tags",
            new_name="hashtags",
        ),
        migrations.RenameField(
            model_name="post", old_name="additional_tags", new_name="hashtags",
        ),
    ]