# Generated by Django 2.2.2 on 2019-07-21 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20190721_0721'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='email_notifications',
            new_name='email_preferences',
        ),
    ]
