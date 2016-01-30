# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0003_auto_20160124_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='status',
            field=models.CharField(max_length=20, choices=[('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed'), ('paused', 'Paused')], default='scheduled'),
        ),
    ]
