# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0008_auto_20160103_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='icon',
            field=filebrowser.fields.FileBrowseField(max_length=200, null=True, blank=True, verbose_name='Image'),
        ),
        migrations.AddField(
            model_name='topic',
            name='introduction',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='external_primary_image',
            field=models.URLField(max_length=500, blank=True, help_text='If the primary image has a value, it overrides this.'),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(max_length=20, default='large', choices=[('admin_thumbnail', 'admin_thumbnail'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('small', 'small'), ('large', 'large'), ('medium', 'medium'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed."),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(max_length=20, default='big', choices=[('admin_thumbnail', 'admin_thumbnail'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('small', 'small'), ('large', 'large'), ('medium', 'medium'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed."),
        ),
    ]
