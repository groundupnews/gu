# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagulous.models.models
import tagulous.models.fields
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(blank=True, max_length=200)),
                ('summary_image', filebrowser.fields.FileBrowseField(blank=True, max_length=200, null=True, verbose_name='Image')),
                ('summary_image_size', models.CharField(default='big', choices=[('medium', 'medium'), ('thumbnail', 'thumbnail'), ('large', 'large'), ('admin_thumbnail', 'admin_thumbnail'), ('big', 'big'), ('small', 'small'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20)),
                ('summary_text', models.TextField(blank=True)),
                ('byline', models.CharField(blank=True, max_length=200, help_text='If this is not blank it overrides the value of the author fields', verbose_name='customised byline')),
                ('primary_image', filebrowser.fields.FileBrowseField(blank=True, null=True, max_length=200)),
                ('primary_image_size', models.CharField(default='large', choices=[('medium', 'medium'), ('thumbnail', 'thumbnail'), ('large', 'large'), ('admin_thumbnail', 'admin_thumbnail'), ('big', 'big'), ('small', 'small'), ('LEAVE', 'LEAVE')], help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20)),
                ('external_primary_image', models.URLField(blank=True)),
                ('primary_image_caption', models.CharField(blank=True, max_length=400)),
                ('body', models.TextField(blank=True)),
                ('published', models.DateTimeField(blank=True, null=True, verbose_name='publish time')),
                ('copyright', models.TextField(blank=True, default='&copy; 2016 GroundUp. <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nd/4.0/80x15.png" /></a><br />This article is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/">Creative Commons Attribution-NoDerivatives 4.0 International License</a>.')),
                ('template', models.CharField(default='newsroom/article_detail.html', choices=[('newsroom/article_detail.html', 'Standard')], max_length=200)),
                ('summary_template', models.CharField(default='newsroom/article_summary.html', choices=[('newsroom/article_summary.html', 'Standard'), ('newsroom/photo_summary.html', 'Great Photo'), ('newsroom/text_summary.html', 'Text only')], max_length=200)),
                ('include_in_rss', models.BooleanField(default=True)),
                ('comments_on', models.BooleanField(default=True)),
                ('exclude_from_list_views', models.BooleanField(default=False)),
                ('stickiness', models.IntegerField(default=0, help_text='The higher the value, the stickier the article.')),
                ('slug', models.SlugField(unique=True, max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('cached_byline', models.CharField(blank=True, max_length=200)),
                ('cached_byline_no_links', models.CharField(blank=True, max_length=200, verbose_name='Byline')),
                ('cached_primary_image', models.URLField(blank=True)),
                ('cached_summary_image', models.URLField(blank=True)),
                ('cached_summary_text', models.TextField(blank=True)),
                ('cached_summary_text_no_html', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-stickiness', '-published'],
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('first_names', models.CharField(blank=True, max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('title', models.CharField(blank=True, max_length=20)),
                ('photo', filebrowser.fields.FileBrowseField(blank=True, null=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('twitter', models.CharField(blank=True, max_length=200)),
                ('facebook', models.CharField(blank=True, max_length=200)),
                ('googleplus', models.CharField(blank=True, max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('email_is_private', models.BooleanField(default=True)),
                ('telephone', models.CharField(blank=True, max_length=200)),
                ('cell', models.CharField(blank=True, max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['last_name', 'first_names'],
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=255)),
                ('slug', models.SlugField()),
                ('count', models.IntegerField(default=0, help_text='Internal counter of how many times this tag is in use')),
                ('protected', models.BooleanField(default=False, help_text='Will not be deleted when the count reaches 0')),
            ],
            options={
                'verbose_name_plural': 'categories',
                'verbose_name': 'category',
            },
            bases=(tagulous.models.models.BaseTagModel, models.Model),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=255)),
                ('slug', models.SlugField()),
                ('count', models.IntegerField(default=0, help_text='Internal counter of how many times this tag is in use')),
                ('protected', models.BooleanField(default=False, help_text='Will not be deleted when the count reaches 0')),
                ('path', models.TextField(unique=True)),
                ('label', models.CharField(help_text='The name of the tag, without ancestors', max_length=255)),
                ('level', models.IntegerField(default=1, help_text='The level of the tag in the tree')),
                ('parent', models.ForeignKey(to='newsroom.Region', related_name='children', null=True, blank=True)),
            ],
            options={
                'abstract': False,
                'ordering': ('name',),
            },
            bases=(tagulous.models.models.BaseTagTreeModel, models.Model),
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(unique=True, max_length=255)),
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
            name='topic',
            unique_together=set([('slug',)]),
        ),
        migrations.AddField(
            model_name='article',
            name='author_01',
            field=models.ForeignKey(to='newsroom.Author', related_name='author_01', null=True, blank=True, verbose_name='first author'),
        ),
        migrations.AddField(
            model_name='article',
            name='author_02',
            field=models.ForeignKey(to='newsroom.Author', related_name='author_02', null=True, blank=True, verbose_name='second author'),
        ),
        migrations.AddField(
            model_name='article',
            name='author_03',
            field=models.ForeignKey(to='newsroom.Author', related_name='author_03', null=True, blank=True, verbose_name='third author'),
        ),
        migrations.AddField(
            model_name='article',
            name='author_04',
            field=models.ForeignKey(to='newsroom.Author', related_name='author_04', null=True, blank=True, verbose_name='fourth author'),
        ),
        migrations.AddField(
            model_name='article',
            name='author_05',
            field=models.ForeignKey(to='newsroom.Author', related_name='author_05', null=True, blank=True, verbose_name='fifth author'),
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=tagulous.models.fields.SingleTagField(to='newsroom.Category', default=4, null=True, _set_tag_meta=True, case_sensitive=False, blank=True, initial='Brief, News, Feature, Photo Essay, Analysis, Opinion, Photo', space_delimiter=False),
        ),
        migrations.AddField(
            model_name='article',
            name='region',
            field=tagulous.models.fields.SingleTagField(to='newsroom.Region', null=True, _set_tag_meta=True, case_sensitive=False, blank=True, tree=True),
        ),
        migrations.AddField(
            model_name='article',
            name='topics',
            field=tagulous.models.fields.TagField(max_count=8, to='newsroom.Topic', help_text='Enter a comma-separated tag string', _set_tag_meta=True, case_sensitive=False, blank=True, space_delimiter=False),
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([('slug', 'parent')]),
        ),
    ]
