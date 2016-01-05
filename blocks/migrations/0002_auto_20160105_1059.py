# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('blocks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='block',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 5, 8, 58, 56, 629486, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='group',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 5, 8, 59, 3, 236954, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
