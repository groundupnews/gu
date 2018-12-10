# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0005_auto_20160314_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='activate_slideshow',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='article',
            name='additional_body_scripts',
            field=models.TextField(help_text='Include things like additional javascript that should come at bottom of article', blank=True),
        ),
        migrations.AddField(
            model_name='article',
            name='additional_head_scripts',
            field=models.TextField(blank=True),
        ),
    ]
