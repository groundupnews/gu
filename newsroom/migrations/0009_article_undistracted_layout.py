# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0008_auto_20160325_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='undistracted_layout',
            field=models.BooleanField(default=False),
        ),
    ]
