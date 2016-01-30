# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0020_auto_20160130_1448'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='faceook_send_status',
        ),
        migrations.AddField(
            model_name='article',
            name='facebook_send_status',
            field=models.CharField(choices=[('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed'), ('paused', 'Paused')], max_length=20, verbose_name='sent status', default='paused'),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(null=True, related_name='main', help_text="Used for generating 'See also' list of articles.", case_sensitive=False, protect_all=True, to='newsroom.Topic', space_delimiter=False, blank=True, _set_tag_meta=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo'),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(blank=True, case_sensitive=False, protect_all=True, to='newsroom.Topic', space_delimiter=False, help_text='Enter a comma-separated tag string', _set_tag_meta=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', max_count=8),
        ),
    ]
