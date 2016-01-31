# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0004_auto_20160130_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='tag_accounts',
            field=tagulous.models.fields.TagField(blank=True, max_count=8, case_sensitive=False, to='socialmedia.TwitterHandle', _set_tag_meta=True, protect_all=True, help_text='Enter a comma-separated tag string', space_delimiter=True),
        ),
    ]
