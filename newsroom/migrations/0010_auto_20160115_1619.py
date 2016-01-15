# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0009_auto_20160115_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='template',
            field=models.CharField(max_length=200, default='newsroom/topic_detail.html'),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", choices=[('large', 'large'), ('big', 'big'), ('medium', 'medium'), ('thumbnail', 'thumbnail'), ('admin_thumbnail', 'admin_thumbnail'), ('small', 'small'), ('LEAVE', 'LEAVE')], max_length=20, default='large'),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", choices=[('large', 'large'), ('big', 'big'), ('medium', 'medium'), ('thumbnail', 'thumbnail'), ('admin_thumbnail', 'admin_thumbnail'), ('small', 'small'), ('LEAVE', 'LEAVE')], max_length=20, default='big'),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(blank=True, _set_tag_meta=True, space_delimiter=False, to='newsroom.Topic', case_sensitive=False, help_text='Enter a comma-separated tag string', max_count=8),
        ),
    ]
