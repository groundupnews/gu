# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filebrowser.fields
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0019_auto_20160124_2333'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='facebook_description',
            field=models.TextField(blank=True, help_text='Leave blank to use same text as summary.'),
        ),
        migrations.AddField(
            model_name='article',
            name='facebook_image',
            field=filebrowser.fields.FileBrowseField(max_length=200, null=True, verbose_name='image', blank=True, help_text='Leave blank to use primary image.'),
        ),
        migrations.AddField(
            model_name='article',
            name='facebook_image_caption',
            field=models.CharField(max_length=200, verbose_name='caption', blank=True, help_text='Leave blank to use primary image caption.'),
        ),
        migrations.AddField(
            model_name='article',
            name='facebook_message',
            field=models.TextField(verbose_name='message', blank=True, help_text='Longer status update that appears above the image in Facebook. '),
        ),
        migrations.AddField(
            model_name='article',
            name='facebook_wait_time',
            field=models.PositiveIntegerField(default=0, help_text='Minimum number of minutes after publication till post.'),
        ),
        migrations.AddField(
            model_name='article',
            name='faceook_send_status',
            field=models.CharField(max_length=20, choices=[('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed'), ('paused', 'Paused')], verbose_name='sent status', default='scheduled'),
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(to='newsroom.Category', case_sensitive=False, null=True, space_delimiter=False, _set_tag_meta=True, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', protect_all=True, blank=True, default=4),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(to='newsroom.Topic', related_name='main', case_sensitive=False, null=True, space_delimiter=False, _set_tag_meta=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', protect_all=True, blank=True, help_text="Used for generating 'See also' list of articles."),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(to='newsroom.Topic', case_sensitive=False, space_delimiter=False, _set_tag_meta=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', protect_all=True, max_count=8, blank=True, help_text='Enter a comma-separated tag string'),
        ),
    ]
