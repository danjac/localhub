# Generated by Django 2.2 on 2019-05-05 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('likes', '0002_auto_20190505_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='object_id',
            field=models.PositiveIntegerField(db_index=True),
        ),
    ]
