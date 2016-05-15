# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0010_article_collapse_comments'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='author',
            unique_together=set([('first_names', 'last_name')]),
        ),
    ]
