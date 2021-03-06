# Generated by Django 3.0.5 on 2020-04-23 03:12

# Django
import django.contrib.postgres.indexes
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("private_messages", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="recipient",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="received_messages",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sent_messages",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name="message",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_document"], name="private_mes_search__c13cc0_gin"
            ),
        ),
        migrations.AddIndex(
            model_name="message",
            index=models.Index(
                fields=["created", "-created", "read"],
                name="private_mes_created_d71833_idx",
            ),
        ),
    ]
