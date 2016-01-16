# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0013_auto_20160116_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='recommended',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='primary_image_size',
            field=models.CharField(max_length=20, default='large', help_text="Choose 'LEAVE' if image size should not be changed."),
        ),
        migrations.AlterField(
            model_name='article',
            name='summary_image_size',
            field=models.CharField(max_length=20, default='big', help_text="Choose 'LEAVE' if image size should not be changed."),
        ),
    ]
