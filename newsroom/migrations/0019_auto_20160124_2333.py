# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0018_auto_20160124_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(_set_tag_meta=True, null=True, protect_all=True, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', to='newsroom.Category', case_sensitive=False, default=4, space_delimiter=False, blank=True),
        ),
    ]
