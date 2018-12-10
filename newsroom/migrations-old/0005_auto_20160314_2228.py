# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0004_article_promote_article'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='promote_article',
            field=models.BooleanField(default=True),
        ),
    ]
