# Generated by Django 2.2.4 on 2019-09-06 10:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def delete_join_requests_without_sender(apps, schema_editor):
    JoinRequest = apps.get_model("join_requests.JoinRequest")
    JoinRequest.objects.using(schema_editor.connection.alias).filter(
        sender__isnull=True
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("communities", "0013_auto_20190906_0526"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("join_requests", "0003_auto_20190811_2142"),
    ]

    operations = [
        migrations.RunPython(delete_join_requests_without_sender),
        migrations.AlterField(
            model_name="joinrequest",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterUniqueTogether(
            name="joinrequest", unique_together={("community", "sender")}
        ),
        migrations.RemoveField(model_name="joinrequest", name="email"),
    ]
