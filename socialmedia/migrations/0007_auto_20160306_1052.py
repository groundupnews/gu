# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0006_auto_20160202_0103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='tag_accounts',
            field=tagulous.models.fields.TagField(case_sensitive=False, space_delimiter=True, blank=True, help_text='Enter a comma-separated tag string', protect_all=True, max_count=8, _set_tag_meta=True, to='socialmedia.TwitterHandle'),
        ),
    ]
