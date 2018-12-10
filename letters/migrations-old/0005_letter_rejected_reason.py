# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0004_auto_20160501_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='rejected_reason',
            field=models.TextField(blank=True),
        ),
    ]
