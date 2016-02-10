# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0027_auto_20160208_2220'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useredit',
            options={'ordering': ['article', 'edit_time']},
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(case_sensitive=False, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', blank=True, to='newsroom.Category', _set_tag_meta=True, default=4, space_delimiter=False, null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(blank=True, to='newsroom.Topic', _set_tag_meta=True, space_delimiter=False, case_sensitive=False, help_text="Used for generating 'See also' list of articles.", related_name='main', null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(help_text='Enter a comma-separated tag string', max_count=8, blank=True, to='newsroom.Topic', _set_tag_meta=True, space_delimiter=False, case_sensitive=False),
        ),
        migrations.AlterUniqueTogether(
            name='useredit',
            unique_together=set([('article', 'user')]),
        ),
    ]
