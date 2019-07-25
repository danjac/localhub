# Generated by Django 2.2.2 on 2019-07-20 10:00

from django.conf import settings
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import localhub.core.markdown.fields
import model_utils.fields
import simple_history.models
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0007_community_content_warning_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0007_remove_event_editor'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalEvent',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', localhub.core.markdown.fields.MarkdownField(blank=True)),
                ('search_document', django.contrib.postgres.search.SearchVectorField(editable=False, null=True)),
                ('title', models.CharField(max_length=200)),
                ('url', models.URLField(blank=True, null=True, verbose_name='Link')),
                ('starts', models.DateTimeField(verbose_name='Starts on (UTC)')),
                ('ends', models.DateTimeField(blank=True, null=True)),
                ('timezone', timezone_field.fields.TimeZoneField(default='UTC')),
                ('venue', models.CharField(blank=True, max_length=200)),
                ('street_address', models.CharField(blank=True, max_length=200)),
                ('locality', models.CharField(blank=True, max_length=200, verbose_name='City or town')),
                ('postal_code', models.CharField(blank=True, max_length=20)),
                ('region', models.CharField(blank=True, max_length=200)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('ticket_price', models.CharField(blank=True, max_length=200)),
                ('ticket_vendor', models.TextField(blank=True, verbose_name='Tickets available from')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('community', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='communities.Community')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical event',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
