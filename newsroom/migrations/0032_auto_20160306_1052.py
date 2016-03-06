# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0031_auto_20160306_1044'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([]),
        ),
    ]
