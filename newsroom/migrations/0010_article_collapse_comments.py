# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0009_article_undistracted_layout'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='collapse_comments',
            field=models.BooleanField(default=True),
        ),
    ]
