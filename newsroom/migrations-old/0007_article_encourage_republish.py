# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0006_auto_20160322_1413'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='encourage_republish',
            field=models.BooleanField(default=True),
        ),
    ]
