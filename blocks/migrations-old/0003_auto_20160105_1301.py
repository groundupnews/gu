# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blocks', '0002_auto_20160105_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blockgroup',
            name='block',
            field=models.ForeignKey(related_name='link_to_group', to='blocks.Block'),
        ),
    ]
