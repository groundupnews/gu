# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0002_auto_20160124_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='characters_left',
            field=models.IntegerField(default=117),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='tweet_text',
            field=models.CharField(max_length=117, blank=True),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='wait_time',
            field=models.PositiveIntegerField(help_text='Number of minutes after publication till tweet.'),
        ),
    ]
