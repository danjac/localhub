# Generated by Django 3.0.5 on 2020-04-22 21:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("comments", "0011_auto_20200318_1112"),
    ]

    operations = [
        migrations.DeleteModel(name="HistoricalComment",),
    ]