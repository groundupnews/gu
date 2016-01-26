# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='wait_time',
            field=models.PositiveIntegerField(help_text='Number of minutes (roughly) after publication that tweet should be sent.'),
        ),
    ]
