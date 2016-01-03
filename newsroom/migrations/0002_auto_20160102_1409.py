# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(default='large', choices=[('small', 'small'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('large', 'large'), ('admin_thumbnail', 'admin_thumbnail'), ('medium', 'medium'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(default='big', choices=[('small', 'small'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('large', 'large'), ('admin_thumbnail', 'admin_thumbnail'), ('medium', 'medium'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(space_delimiter=False, case_sensitive=False, max_count=8, _set_tag_meta=True, help_text='Enter a comma-separated tag string', initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', to='newsroom.Topic', blank=True),
        ),
    ]
