# Generated by Django 3.0.5 on 2020-05-02 10:13

# Django
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0004_auto_20200426_1805"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="event",
            name="contact_email",
        ),
        migrations.RemoveField(
            model_name="event",
            name="contact_name",
        ),
        migrations.RemoveField(
            model_name="event",
            name="contact_phone",
        ),
        migrations.RemoveField(
            model_name="event",
            name="ticket_price",
        ),
        migrations.RemoveField(
            model_name="event",
            name="ticket_vendor",
        ),
    ]
