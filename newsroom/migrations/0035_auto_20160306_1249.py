# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0034_auto_20160306_1248'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together=set([]),
        ),
    ]
