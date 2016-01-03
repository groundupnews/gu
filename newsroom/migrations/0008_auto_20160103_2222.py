# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0007_auto_20160103_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='disqus_id',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(default='large', choices=[('thumbnail', 'thumbnail'), ('admin_thumbnail', 'admin_thumbnail'), ('small', 'small'), ('medium', 'medium'), ('big', 'big'), ('large', 'large'), ('LEAVE', 'LEAVE')], max_length=20, help_text="Choose 'LEAVE' if image size should not be changed."),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(default='big', choices=[('thumbnail', 'thumbnail'), ('admin_thumbnail', 'admin_thumbnail'), ('small', 'small'), ('medium', 'medium'), ('big', 'big'), ('large', 'large'), ('LEAVE', 'LEAVE')], max_length=20, help_text="Choose 'LEAVE' if image size should not be changed."),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(max_count=8, blank=True, space_delimiter=False, help_text='Enter a comma-separated tag string', to='newsroom.Topic', _set_tag_meta=True, case_sensitive=False, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo'),
        ),
    ]
