# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0023_auto_20160131_0107'),
    ]

    operations = [
        migrations.CreateModel(
            name='MostPopular',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('article_list', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', default=4, _set_tag_meta=True, null=True, case_sensitive=False, blank=True, space_delimiter=False, to='newsroom.Category'),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(_set_tag_meta=True, null=True, help_text="Used for generating 'See also' list of articles.", space_delimiter=False, blank=True, related_name='main', case_sensitive=False, to='newsroom.Topic'),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(_set_tag_meta=True, case_sensitive=False, help_text='Enter a comma-separated tag string', max_count=8, blank=True, space_delimiter=False, to='newsroom.Topic'),
        ),
    ]
