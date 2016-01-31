# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0022_auto_20160130_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(case_sensitive=False, blank=True, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', null=True, to='newsroom.Category', _set_tag_meta=True, default=4, space_delimiter=False, protect_all=True),
        ),
    ]
