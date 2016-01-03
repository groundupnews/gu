# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0003_auto_20160102_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='primary_image_caption',
            field=models.CharField(max_length=600, blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(default='large', max_length=20, help_text="Choose 'LEAVE' if image size should not be changed.", choices=[('large', 'large'), ('thumbnail', 'thumbnail'), ('medium', 'medium'), ('admin_thumbnail', 'admin_thumbnail'), ('big', 'big'), ('small', 'small'), ('LEAVE', 'LEAVE')]),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(default='big', max_length=20, help_text="Choose 'LEAVE' if image size should not be changed.", choices=[('large', 'large'), ('thumbnail', 'thumbnail'), ('medium', 'medium'), ('admin_thumbnail', 'admin_thumbnail'), ('big', 'big'), ('small', 'small'), ('LEAVE', 'LEAVE')]),
        ),
    ]
