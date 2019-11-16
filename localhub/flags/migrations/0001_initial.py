# Generated by Django 2.2.2 on 2019-06-25 07:48

import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('communities', '0004_auto_20190602_1838'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('object_id', models.PositiveIntegerField()),
                ('reason', models.CharField(choices=[('spam', 'Spam'), ('abuse', 'Abuse'), ('rules', 'Breach of community rules'), ('illegal_activity', 'Illegal activity'), ('pornography', 'Pornography'), ('copyright', 'Breach of copyright')], default='spam', max_length=30)),
                ('community', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='communities.Community')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('moderator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='flag',
            constraint=models.UniqueConstraint(fields=('user', 'content_type', 'object_id'), name='unique_flag'),
        ),
    ]
