# Generated by Django 2.2.2 on 2019-07-30 20:23

from django.conf import settings
from django.db import migrations, models
import localhub.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('users', '0018_auto_20190729_2118'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='blacklisted_tags',
        ),
        migrations.AddField(
            model_name='user',
            name='blocked_tags',
            field=models.ManyToManyField(blank=True, related_name='_user_blocked_tags_+', to='taggit.Tag'),
        ),
        migrations.AlterField(
            model_name='user',
            name='blocked',
            field=models.ManyToManyField(blank=True, related_name='blockers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='user',
            name='email_preferences',
            field=localhub.core.fields.ChoiceArrayField(base_field=models.CharField(choices=[('messages', 'I receive a direct message'), ('follows', 'Someone starts following me'), ('comments', 'Someone comments on my post'), ('mentions', 'I am @mentioned in a post or comment'), ('deletes', 'A moderator deletes my post or comment'), ('edits', 'A moderator edits my post or comment'), ('followings', "Someone I'm following creates a post"), ('likes', 'Someone likes my post or comment'), ('tags', "A post is created containing tags I'm following"), ('flags', 'Post or comment is flagged (MODERATORS ONLY)'), ('reviews', 'Content to be reviewed (MODERATORS ONLY)')], max_length=12), blank=True, default=list, size=None),
        ),
        migrations.AlterField(
            model_name='user',
            name='following',
            field=models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL),
        ),
    ]
