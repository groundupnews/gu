# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0017_auto_20160124_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(blank=True, to='newsroom.Category', protect_all=True, default=4, _set_tag_meta=True, null=True, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', space_delimiter=True, case_sensitive=False),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(blank=True, null=True, related_name='main', help_text="Used for generating 'See also' list of articles.", protect_all=True, space_delimiter=False, case_sensitive=False, _set_tag_meta=True, to='newsroom.Topic'),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(blank=True, to='newsroom.Topic', _set_tag_meta=True, max_count=8, help_text='Enter a comma-separated tag string', protect_all=True, space_delimiter=False, case_sensitive=False),
        ),
    ]
