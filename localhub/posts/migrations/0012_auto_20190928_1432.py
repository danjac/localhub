# Generated by Django 2.2.5 on 2019-09-28 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0011_auto_20190812_0720'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalpost',
            name='metadata_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='historicalpost',
            name='metadata_image',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='post',
            name='metadata_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='post',
            name='metadata_image',
            field=models.URLField(blank=True),
        ),
    ]
