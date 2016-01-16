# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0010_auto_20160115_1619'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(null=True, to='newsroom.Topic', case_sensitive=False, space_delimiter=False, _set_tag_meta=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', help_text="Used for generating 'See also' list of article", blank=True, related_name='main'),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20, choices=[('admin_thumbnail', 'admin_thumbnail'), ('medium', 'medium'), ('big', 'big'), ('thumbnail', 'thumbnail'), ('large', 'large'), ('small', 'small'), ('LEAVE', 'LEAVE')], default='large'),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20, choices=[('admin_thumbnail', 'admin_thumbnail'), ('medium', 'medium'), ('big', 'big'), ('thumbnail', 'thumbnail'), ('large', 'large'), ('small', 'small'), ('LEAVE', 'LEAVE')], default='big'),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(space_delimiter=False, to='newsroom.Topic', _set_tag_meta=True, case_sensitive=False, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', help_text='Enter a comma-separated tag string', blank=True, max_count=8),
        ),
        migrations.AlterField(
            model_name='topic',
            name='introduction',
            field=models.TextField(help_text='Use unfiltered HTML. If this is not blank, the default template does not render any other fields before the article list.', blank=True),
        ),
    ]
