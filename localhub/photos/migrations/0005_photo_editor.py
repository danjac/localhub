# Generated by Django 2.2.2 on 2019-07-19 22:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('photos', '0004_auto_20190709_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='editor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
