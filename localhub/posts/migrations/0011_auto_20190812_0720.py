# Generated by Django 2.2.4 on 2019-08-12 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20190801_0717'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='post',
            name='posts_post_owner_i_f616f0_idx',
        ),
        migrations.AddIndex(
            model_name='post',
            index=models.Index(fields=['created', '-created'], name='posts_post_created_f1ee68_idx'),
        ),
    ]
