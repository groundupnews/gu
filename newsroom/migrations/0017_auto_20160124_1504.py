# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0016_auto_20160118_2135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='primary_image_alt',
            field=models.CharField(max_length=200, blank=True, help_text='Description of image for assistive technology.'),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_alt',
            field=models.CharField(max_length=200, blank=True, help_text='Description of image for assistive technology.'),
        ),
    ]
