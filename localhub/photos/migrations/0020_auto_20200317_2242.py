# Generated by Django 3.0.4 on 2020-03-17 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0019_auto_20200306_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalphoto',
            name='deleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='deleted',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
