# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0028_auto_20160208_2226'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'category', 'verbose_name_plural': 'categories', 'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='useredit',
            options={'ordering': ['article__published', 'edit_time']},
        ),
        migrations.RemoveField(
            model_name='category',
            name='count',
        ),
        migrations.RemoveField(
            model_name='category',
            name='protected',
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.ForeignKey(to='newsroom.Category', default=4),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=200),
        ),
    ]
