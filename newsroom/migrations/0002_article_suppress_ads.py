# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='suppress_ads',
            field=models.BooleanField(help_text='Only suppresses ads that are external to article. You can still create ads in article.', default=True),
        ),
    ]
