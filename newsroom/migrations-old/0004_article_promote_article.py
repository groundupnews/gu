# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0003_auto_20160314_1549'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='promote_article',
            field=models.BooleanField(default=False),
        ),
    ]
