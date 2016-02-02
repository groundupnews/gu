# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0024_auto_20160131_1942'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mostpopular',
            options={'verbose_name_plural': 'most popular'},
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(default=4, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', protect_all=True, to='newsroom.Category', case_sensitive=False, _set_tag_meta=True, blank=True, null=True, space_delimiter=False),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(related_name='main', protect_all=True, to='newsroom.Topic', case_sensitive=False, _set_tag_meta=True, blank=True, null=True, space_delimiter=False, help_text="Used for generating 'See also' list of articles."),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(max_count=8, blank=True, to='newsroom.Topic', case_sensitive=False, _set_tag_meta=True, protect_all=True, space_delimiter=False, help_text='Enter a comma-separated tag string'),
        ),
    ]
