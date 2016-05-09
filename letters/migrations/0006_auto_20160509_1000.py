# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0005_letter_rejected_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='letter',
            name='position',
            field=models.IntegerField(default=0),
        ),
    ]
