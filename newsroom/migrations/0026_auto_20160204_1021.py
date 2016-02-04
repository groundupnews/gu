# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('newsroom', '0025_auto_20160202_0103'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=1),
        ),
        migrations.AddField(
            model_name='article',
            name='version',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(space_delimiter=False, _set_tag_meta=True, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', blank=True, default=4, null=True, to='newsroom.Category', case_sensitive=False),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(help_text="Used for generating 'See also' list of articles.", space_delimiter=False, _set_tag_meta=True, blank=True, to='newsroom.Topic', null=True, case_sensitive=False, related_name='main'),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(help_text='Enter a comma-separated tag string', space_delimiter=False, _set_tag_meta=True, blank=True, to='newsroom.Topic', max_count=8, case_sensitive=False),
        ),
    ]
