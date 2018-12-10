# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import republisher.models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Republisher',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('email_addresses', models.CharField(max_length=250, validators=[republisher.models.validate_email_list])),
                ('message', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RepublisherArticle',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('wait_time', models.PositiveIntegerField(help_text='Minimum number of minutes after publication till sent.', default=0)),
                ('note', models.TextField(blank=True, help_text='A note for the republisher specific to this article.')),
                ('status', models.CharField(max_length=20, default='scheduled', choices=[('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed'), ('paused', 'Paused')])),
                ('article', models.ForeignKey(to='newsroom.Article')),
                ('republisher', models.ForeignKey(to='republisher.Republisher')),
            ],
            options={
                'ordering': ['article__published', 'republisher'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='republisherarticle',
            unique_together=set([('article', 'republisher')]),
        ),
    ]
