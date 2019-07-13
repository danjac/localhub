# Generated by Django 2.2.2 on 2019-07-13 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messageboard', '0002_auto_20190713_1442'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='messagerecipient',
            constraint=models.UniqueConstraint(fields=('recipient', 'message'), name='unique_message_recipient'),
        ),
    ]
