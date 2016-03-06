# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0009_auto_20160306_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='tag_accounts',
            field=models.ManyToManyField(blank=True, to='socialmedia.TwitterHandle'),
        ),
    ]
