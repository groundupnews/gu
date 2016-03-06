# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0008_auto_20160306_1132'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='twitterhandle',
            unique_together=set([]),
        ),
    ]
