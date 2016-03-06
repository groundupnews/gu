# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0029_auto_20160306_0056'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='region',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='article',
            name='region',
            field=models.ForeignKey(to='newsroom.Region', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='region',
            name='slug',
            field=models.SlugField(max_length=200),
        ),
        #migrations.AlterUniqueTogether(
        #    name='region',
        #    unique_together=set([]),
        #),
        migrations.RemoveField(
            model_name='region',
            name='count',
        ),
        migrations.RemoveField(
            model_name='region',
            name='label',
        ),
        migrations.RemoveField(
            model_name='region',
            name='level',
        ),
        migrations.RemoveField(
            model_name='region',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='region',
            name='path',
        ),
        migrations.RemoveField(
            model_name='region',
            name='protected',
        ),
    ]
