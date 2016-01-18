# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0015_auto_20160118_2005'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='cached_small_image',
            field=models.URLField(max_length=500, blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(related_name='main', space_delimiter=False, help_text="Used for generating 'See also' list of articles.", to='newsroom.Topic', null=True, case_sensitive=False, blank=True, _set_tag_meta=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(space_delimiter=False, help_text='Enter a comma-separated tag string', to='newsroom.Topic', _set_tag_meta=True, max_count=8, case_sensitive=False, blank=True),
        ),
    ]
