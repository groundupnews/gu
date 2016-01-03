# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0002_auto_20160102_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='cached_primary_image',
            field=models.URLField(blank=True, max_length=280),
        ),
        migrations.AlterField(
            model_name='article',
            name='cached_summary_image',
            field=models.URLField(blank=True, max_length=280),
        ),
        migrations.AlterField(
            model_name='article',
            name='external_primary_image',
            field=models.URLField(blank=True, max_length=280),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", default='large', choices=[('medium', 'medium'), ('admin_thumbnail', 'admin_thumbnail'), ('small', 'small'), ('big', 'big'), ('large', 'large'), ('thumbnail', 'thumbnail'), ('LEAVE', 'LEAVE')], max_length=20),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", default='big', choices=[('medium', 'medium'), ('admin_thumbnail', 'admin_thumbnail'), ('small', 'small'), ('big', 'big'), ('large', 'large'), ('thumbnail', 'thumbnail'), ('LEAVE', 'LEAVE')], max_length=20),
        ),
    ]
