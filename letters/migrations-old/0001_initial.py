# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0010_article_collapse_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='Letter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('byline', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField(blank=True)),
                ('rejected', models.BooleanField(default=False)),
                ('css_classes', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('published', models.DateTimeField(null=True, verbose_name='publish time', blank=True)),
                ('position', models.PositiveIntegerField(default=0)),
                ('article', models.ForeignKey(to='newsroom.Article')),
            ],
            options={
                'ordering': ['article', 'position'],
            },
        ),
    ]
