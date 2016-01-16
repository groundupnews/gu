# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0012_auto_20160116_0905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(related_name='main', null=True, _set_tag_meta=True, to='newsroom.Topic', initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', blank=True, space_delimiter=False, case_sensitive=False, help_text="Used for generating 'See also' list of articles."),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(max_length=20, default='large', choices=[('big', 'big'), ('admin_thumbnail', 'admin_thumbnail'), ('large', 'large'), ('medium', 'medium'), ('small', 'small'), ('thumbnail', 'thumbnail'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed."),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(max_length=20, default='big', choices=[('big', 'big'), ('admin_thumbnail', 'admin_thumbnail'), ('large', 'large'), ('medium', 'medium'), ('small', 'small'), ('thumbnail', 'thumbnail'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed."),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(space_delimiter=False, case_sensitive=False, _set_tag_meta=True, max_count=8, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', to='newsroom.Topic', help_text='Enter a comma-separated tag string', blank=True),
        ),
    ]
