# Generated by Django 2.2.4 on 2019-08-31 15:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('private_messages', '0004_remove_message_parent'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='private_messages.Message'),
        ),
    ]
