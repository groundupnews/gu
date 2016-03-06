# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0033_auto_20160306_1131'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=models.ForeignKey(blank=True, help_text="Used for generating'See also' list of articles.", to='newsroom.Topic', related_name='main', null=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=models.ManyToManyField(blank=True, to='newsroom.Topic'),
        ),
        migrations.AlterField(
            model_name='topic',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='topic',
            name='slug',
            field=models.SlugField(max_length=200, unique=True),
        ),
        #migrations.AlterUniqueTogether(
        #    name='topic',
        #    unique_together=set([]),
        #),
        migrations.RemoveField(
            model_name='topic',
            name='count',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='protected',
        ),
    ]
