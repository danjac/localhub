# Generated by Django 3.0.3 on 2020-03-05 14:56

from django.db import migrations, models

import localhub.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0034_auto_20200115_2246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='home_page_filters',
            field=localhub.db.fields.ChoiceArrayField(base_field=models.CharField(choices=[('users', "Posts, events and photots from people I'm following"), ('tags', "Posts, events and photos containing tags I'm following")], max_length=12), blank=True, default=list, size=None, verbose_name='Stream Filters'),
        ),
    ]