# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0021_auto_20160130_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(_set_tag_meta=True, default=4, to='newsroom.Category', blank=True, space_delimiter=False, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', null=True, case_sensitive=False),
        ),
        migrations.AlterField(
            model_name='article',
            name='facebook_description',
            field=models.CharField(help_text='Leave blank to use same text as summary.', max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(related_name='main', protect_all=True, to='newsroom.Topic', _set_tag_meta=True, blank=True, space_delimiter=False, case_sensitive=False, help_text="Used for generating 'See also' list of articles.", null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(_set_tag_meta=True, protect_all=True, to='newsroom.Topic', blank=True, space_delimiter=False, case_sensitive=False, help_text='Enter a comma-separated tag string', max_count=8),
        ),
    ]
