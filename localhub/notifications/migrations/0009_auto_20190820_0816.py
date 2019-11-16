# Generated by Django 2.2.4 on 2019-08-20 08:16

import django.db.models.deletion
from django.db import migrations, models


def delete_all_subscriptions(apps, schema_editor):
    PushSubscription = apps.get_model("notifications", "PushSubscription")
    PushSubscription.objects.using(
        schema_editor.connection.alias
    ).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0011_auto_20190814_2109"),
        ("notifications", "0008_auto_20190818_2210"),
    ]

    operations = [
        migrations.RunPython(delete_all_subscriptions),
        migrations.RemoveConstraint(
            model_name="pushsubscription", name="unique_push_notification"
        ),
        migrations.AddField(
            model_name="pushsubscription",
            name="community",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="communities.Community",
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name="pushsubscription",
            constraint=models.UniqueConstraint(
                fields=("user", "auth", "p256dh", "community"),
                name="unique_push_notification",
            ),
        ),
    ]
