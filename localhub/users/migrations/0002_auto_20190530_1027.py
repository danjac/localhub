# Generated by Django 2.2 on 2019-05-30 10:27

from django.db import migrations

import localhub.users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', localhub.users.models.UserManager()),
            ],
        ),
    ]
