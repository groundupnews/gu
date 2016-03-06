# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmedia', '0007_auto_20160306_1052'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='twitterhandle',
            options={'verbose_name': 'Twitter handle', 'verbose_name_plural': 'Twitter Handles', 'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='tweet',
            name='tag_accounts',
            field=models.ManyToManyField(blank=True, to='socialmedia.TwitterHandle', null=True),
        ),
        migrations.AlterField(
            model_name='twitterhandle',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='twitterhandle',
            name='slug',
            field=models.SlugField(max_length=200, unique=True),
        ),
        #migrations.AlterUniqueTogether(
        #    name='twitterhandle',
        #    unique_together=set([]),
        #),
        migrations.RemoveField(
            model_name='twitterhandle',
            name='count',
        ),
        migrations.RemoveField(
            model_name='twitterhandle',
            name='protected',
        ),
    ]
