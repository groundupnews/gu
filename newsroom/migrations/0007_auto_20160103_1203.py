# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0006_auto_20160102_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='cached_byline',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='article',
            name='cached_byline_no_links',
            field=models.CharField(blank=True, max_length=400, verbose_name='Byline'),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(max_length=20, help_text="Choose 'LEAVE' if image size should not be changed.", choices=[('admin_thumbnail', 'admin_thumbnail'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('medium', 'medium'), ('large', 'large'), ('small', 'small'), ('LEAVE', 'LEAVE')], default='large'),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(max_length=20, help_text="Choose 'LEAVE' if image size should not be changed.", choices=[('admin_thumbnail', 'admin_thumbnail'), ('thumbnail', 'thumbnail'), ('big', 'big'), ('medium', 'medium'), ('large', 'large'), ('small', 'small'), ('LEAVE', 'LEAVE')], default='big'),
        ),
    ]
