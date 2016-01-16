# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0011_auto_20160116_0027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(space_delimiter=False, case_sensitive=False, blank=True, to='newsroom.Topic', _set_tag_meta=True, help_text="Used for generating 'See also' list of articles.", related_name='main', null=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo'),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20, choices=[('thumbnail', 'thumbnail'), ('large', 'large'), ('admin_thumbnail', 'admin_thumbnail'), ('medium', 'medium'), ('big', 'big'), ('small', 'small'), ('LEAVE', 'LEAVE')], default='large'),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20, choices=[('thumbnail', 'thumbnail'), ('large', 'large'), ('admin_thumbnail', 'admin_thumbnail'), ('medium', 'medium'), ('big', 'big'), ('small', 'small'), ('LEAVE', 'LEAVE')], default='big'),
        ),
    ]
