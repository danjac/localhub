# Generated by Django 2.2.2 on 2019-07-09 20:59

import communikit.core.markdown.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communities', '0005_auto_20190705_1857'),
    ]

    operations = [
        migrations.AddField(
            model_name='community',
            name='terms',
            field=communikit.core.markdown.fields.MarkdownField(blank=True, help_text='Terms and conditions, code of conduct and other membership terms.'),
        ),
    ]
