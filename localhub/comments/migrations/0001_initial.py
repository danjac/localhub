# Generated by Django 2.2.2 on 2019-06-26 09:42

import localhub.common.markdown.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('communities', '0004_auto_20190602_1838'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('object_id', models.PositiveIntegerField()),
                ('content', localhub.common.markdown.fields.MarkdownField()),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communities.Community')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
