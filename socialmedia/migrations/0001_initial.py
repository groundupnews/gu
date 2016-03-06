# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('wait_time', models.PositiveIntegerField(help_text='Number of minutes after publication till tweet.')),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed'), ('paused', 'Paused')], max_length=20, default='scheduled')),
                ('tweet_text', models.CharField(max_length=117, blank=True)),
                ('image', filebrowser.fields.FileBrowseField(blank=True, max_length=200, null=True)),
                ('characters_left', models.IntegerField(default=116)),
                ('article', models.ForeignKey(to='newsroom.Article')),
            ],
            options={
                'ordering': ['article__published', 'wait_time'],
            },
        ),
        migrations.CreateModel(
            name='TwitterHandle',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('slug', models.SlugField(unique=True, max_length=200)),
            ],
            options={
                'verbose_name': 'Twitter handle',
                'ordering': ['name'],
                'verbose_name_plural': 'Twitter Handles',
            },
        ),
        migrations.AddField(
            model_name='tweet',
            name='tag_accounts',
            field=models.ManyToManyField(to='socialmedia.TwitterHandle', blank=True),
        ),
    ]
