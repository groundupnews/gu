# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import tagulous.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('newsroom', '0026_auto_20160204_1021'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserEdit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('edit_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(space_delimiter=False, _set_tag_meta=True, case_sensitive=False, null=True, protect_all=True, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', blank=True, default=4, to='newsroom.Category'),
        ),
        migrations.AlterField(
            model_name='article',
            name='main_topic',
            field=tagulous.models.fields.SingleTagField(space_delimiter=False, case_sensitive=False, null=True, to='newsroom.Topic', protect_all=True, initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', help_text="Used for generating 'See also' list of articles.", related_name='main', blank=True, _set_tag_meta=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(space_delimiter=False, max_count=8, case_sensitive=False, _set_tag_meta=True, to='newsroom.Topic', initial='"Photo Essay", Analysis, Brief, Feature, News, Opinion, Photo', help_text='Enter a comma-separated tag string', protect_all=True, blank=True),
        ),
        migrations.AddField(
            model_name='useredit',
            name='article',
            field=models.ForeignKey(to='newsroom.Article'),
        ),
        migrations.AddField(
            model_name='useredit',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
