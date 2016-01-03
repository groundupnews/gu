# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0005_auto_20160102_1447'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(choices=[('small', 'small'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('medium', 'medium'), ('admin_thumbnail', 'admin_thumbnail'), ('large', 'large'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed.", default='large', max_length=20),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(choices=[('small', 'small'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('medium', 'medium'), ('admin_thumbnail', 'admin_thumbnail'), ('large', 'large'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed.", default='big', max_length=20),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(case_sensitive=False, _set_tag_meta=True, help_text='Enter a comma-separated tag string', space_delimiter=False, blank=True, to='newsroom.Topic', max_count=8),
        ),
    ]
