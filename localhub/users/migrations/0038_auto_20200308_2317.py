# Generated by Django 3.0.3 on 2020-03-08 23:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_auto_20200308_2315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='home_page_filters',
            new_name='activity_stream_filters',
        ),
    ]