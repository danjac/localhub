# Generated by Django 2.2.2 on 2019-06-26 09:42

import communikit.core.markdown.fields
from django.conf import settings
import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import sorl.thumbnail.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('communities', '0004_auto_20190602_1838'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', communikit.core.markdown.fields.MarkdownField(blank=True)),
                ('search_document', django.contrib.postgres.search.SearchVectorField(editable=False, null=True)),
                ('title', models.CharField(max_length=300)),
                ('image', sorl.thumbnail.fields.ImageField(upload_to='photos')),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communities.Community')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddIndex(
            model_name='photo',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_document'], name='photos_phot_search__e98fe7_gin'),
        ),
    ]
