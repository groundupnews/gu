# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filebrowser.fields
import tagulous.models.fields
import tagulous.models.models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0017_auto_20160124_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('wait_time', models.IntegerField(help_text='Number of minutes (roughly) after publication that tweet should be sent.')),
                ('status', models.CharField(default='scheduled', choices=[('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed')], max_length=20)),
                ('tweet_text', models.CharField(max_length=140, blank=True)),
                ('image', filebrowser.fields.FileBrowseField(null=True, max_length=200, blank=True)),
                ('article', models.ForeignKey(to='newsroom.Article')),
            ],
            options={
                'ordering': ['article__published', 'wait_time'],
            },
        ),
        migrations.CreateModel(
            name='TwitterHandle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('slug', models.SlugField()),
                ('count', models.IntegerField(default=0, help_text='Internal counter of how many times this tag is in use')),
                ('protected', models.BooleanField(default=False, help_text='Will not be deleted when the count reaches 0')),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
            bases=(tagulous.models.models.BaseTagModel, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='twitterhandle',
            unique_together=set([('slug',)]),
        ),
        migrations.AddField(
            model_name='tweet',
            name='tag_accounts',
            field=tagulous.models.fields.TagField(max_count=8, blank=True, protect_all=True, case_sensitive=False, _set_tag_meta=True, to='socialmedia.TwitterHandle', space_delimiter=True, help_text='Enter a comma-separated tag string'),
        ),
    ]
