# Generated by Django 2.2 on 2019-04-25 18:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0003_auto_20190425_1842'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='community',
            name='site',
        ),
        migrations.AlterField(
            model_name='community',
            name='domain',
            field=models.CharField(max_length=100, unique=True, validators=[django.core.validators.RegexValidator(message='This is not a valid domain', regex='([a-z¡-\uffff0-9](?:[a-z¡-\uffff0-9-]{0,61}[a-z¡-\uffff0-9])?(?:\\.(?!-)[a-z¡-\uffff0-9-]{1,63}(?<!-))*\\.(?!-)(?:[a-z¡-\uffff-]{2,63}|xn--[a-z0-9]{1,59})(?<!-)\\.?|localhost)')]),
        ),
    ]
