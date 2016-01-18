# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0014_auto_20160116_2145'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='primary_image_alt',
            field=models.CharField(max_length=200, blank=True, help_text='Description of image for assisted technology.'),
        ),
        migrations.AddField(
            model_name='article',
            name='summary_image_alt',
            field=models.CharField(max_length=200, blank=True, help_text='Description of image for assisted technology.'),
        ),
        migrations.AddField(
            model_name='article',
            name='use_editor',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(null=True, to='newsroom.Topic', help_text="Used for generating 'See also' list of articles.", _set_tag_meta=True, case_sensitive=False, related_name='main', blank=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', space_delimiter=False),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(_set_tag_meta=True, case_sensitive=False, help_text='Enter a comma-separated tag string', to='newsroom.Topic', blank=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', space_delimiter=False, max_count=8),
        ),
    ]
