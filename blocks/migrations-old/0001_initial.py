# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('html', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='BlockGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('position', models.PositiveSmallIntegerField(null=True, verbose_name='position')),
                ('block', models.ForeignKey(to='blocks.Block')),
            ],
            options={
                'ordering': ['position'],
            },
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('pages_include', models.TextField(blank=True)),
                ('pages_exclude', models.TextField(blank=True)),
                ('blocks', models.ManyToManyField(to='blocks.Block', through='blocks.BlockGroup', blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='blockgroup',
            name='group',
            field=models.ForeignKey(to='blocks.Group'),
        ),
    ]
