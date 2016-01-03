# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0004_auto_20160102_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='cached_primary_image',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='article',
            name='cached_summary_image',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='article',
            name='external_primary_image',
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20, choices=[('medium', 'medium'), ('small', 'small'), ('admin_thumbnail', 'admin_thumbnail'), ('large', 'large'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('LEAVE', 'LEAVE')], default='large'),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20, choices=[('medium', 'medium'), ('small', 'small'), ('admin_thumbnail', 'admin_thumbnail'), ('large', 'large'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('LEAVE', 'LEAVE')], default='big'),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(space_delimiter=False, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', blank=True, help_text='Enter a comma-separated tag string', _set_tag_meta=True, max_count=8, to='newsroom.Topic', case_sensitive=False),
        ),
    ]
