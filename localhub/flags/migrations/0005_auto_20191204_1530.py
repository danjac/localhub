# Generated by Django 2.2.8 on 2019-12-04 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flags', '0004_auto_20190812_0720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flag',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communities.Community'),
        ),
    ]
