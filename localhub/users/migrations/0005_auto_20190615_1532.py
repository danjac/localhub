# Generated by Django 2.2.2 on 2019-06-15 15:32

from django.db import migrations

import localhub.common.markdown.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=localhub.common.markdown.fields.MarkdownField(blank=True),
        ),
    ]
