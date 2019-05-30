# Generated by Django 2.2 on 2019-05-30 09:22

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('communities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JoinRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('status', model_utils.fields.StatusField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], db_index=True, default='pending', max_length=100, no_check_for_status=True)),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status')),
                ('sent', models.DateTimeField(blank=True, null=True)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communities.Community')),
            ],
        ),
    ]
