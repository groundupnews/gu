# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0005_auto_20160131_0107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='characters_left',
            field=models.IntegerField(default=116),
        ),
    ]
