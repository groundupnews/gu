# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filebrowser.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=200)),
                ('subtitle', models.CharField(max_length=200, blank=True)),
                ('summary_image', filebrowser.fields.FileBrowseField(max_length=200, verbose_name='Image', null=True, blank=True)),
                ('summary_image_size', models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20, default='big')),
                ('summary_image_alt', models.CharField(help_text='Description of image for assistive technology.', max_length=200, blank=True)),
                ('summary_text', models.TextField(blank=True)),
                ('byline', models.CharField(help_text='If this is not blank it overrides the value of the author fields', max_length=200, verbose_name='customised byline', blank=True)),
                ('primary_image', filebrowser.fields.FileBrowseField(max_length=200, null=True, blank=True)),
                ('primary_image_size', models.CharField(help_text="Choose 'LEAVE' if image size should not be changed.", max_length=20, default='large')),
                ('primary_image_alt', models.CharField(help_text='Description of image for assistive technology.', max_length=200, blank=True)),
                ('external_primary_image', models.URLField(help_text='If the primary image has a value, it overrides this.', max_length=500, blank=True)),
                ('primary_image_caption', models.CharField(max_length=600, blank=True)),
                ('body', models.TextField(blank=True)),
                ('use_editor', models.BooleanField(default=True)),
                ('published', models.DateTimeField(verbose_name='publish time', null=True, blank=True)),
                ('recommended', models.BooleanField(default=True)),
                ('copyright', models.TextField(default='&copy; 2016 GroundUp. <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nd/4.0/80x15.png" /></a><br />This article is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/">Creative Commons Attribution-NoDerivatives 4.0 International License</a>.', blank=True)),
                ('template', models.CharField(max_length=200, default='newsroom/article_detail.html', choices=[('newsroom/article_detail.html', 'Standard')])),
                ('summary_template', models.CharField(max_length=200, default='newsroom/article_summary.html', choices=[('newsroom/article_summary.html', 'Standard'), ('newsroom/photo_summary.html', 'Great Photo'), ('newsroom/text_summary.html', 'Text only')])),
                ('include_in_rss', models.BooleanField(default=True)),
                ('comments_on', models.BooleanField(default=True)),
                ('exclude_from_list_views', models.BooleanField(default=False)),
                ('disqus_id', models.CharField(max_length=20, blank=True)),
                ('stickiness', models.IntegerField(help_text='The higher the value, the stickier the article.', default=0)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('facebook_wait_time', models.PositiveIntegerField(help_text='Minimum number of minutes after publication till post.', default=0)),
                ('facebook_image', filebrowser.fields.FileBrowseField(help_text='Leave blank to use primary image.', max_length=200, verbose_name='image', null=True, blank=True)),
                ('facebook_image_caption', models.CharField(help_text='Leave blank to use primary image caption.', max_length=200, verbose_name='caption', blank=True)),
                ('facebook_description', models.CharField(help_text='Leave blank to use same text as summary.', max_length=200, blank=True)),
                ('facebook_message', models.TextField(help_text='Longer status update that appears above the image in Facebook. ', verbose_name='message', blank=True)),
                ('facebook_send_status', models.CharField(max_length=20, verbose_name='sent status', default='paused', choices=[('scheduled', 'Scheduled'), ('sent', 'Sent'), ('failed', 'Failed'), ('paused', 'Paused')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('version', models.PositiveIntegerField(default=0)),
                ('cached_byline', models.CharField(max_length=500, blank=True)),
                ('cached_byline_no_links', models.CharField(max_length=400, verbose_name='Byline', blank=True)),
                ('cached_primary_image', models.URLField(max_length=500, blank=True)),
                ('cached_summary_image', models.URLField(max_length=500, blank=True)),
                ('cached_summary_text', models.TextField(blank=True)),
                ('cached_summary_text_no_html', models.TextField(blank=True)),
                ('cached_small_image', models.URLField(max_length=500, blank=True)),
            ],
            options={
                'ordering': ['-stickiness', '-published'],
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('first_names', models.CharField(max_length=200, blank=True)),
                ('last_name', models.CharField(max_length=200)),
                ('title', models.CharField(max_length=20, blank=True)),
                ('photo', filebrowser.fields.FileBrowseField(max_length=200, null=True, blank=True)),
                ('description', models.TextField(blank=True)),
                ('website', models.URLField(blank=True)),
                ('twitter', models.CharField(max_length=200, blank=True)),
                ('facebook', models.CharField(max_length=200, blank=True)),
                ('googleplus', models.CharField(max_length=200, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('email_is_private', models.BooleanField(default=True)),
                ('telephone', models.CharField(max_length=200, blank=True)),
                ('cell', models.CharField(max_length=200, blank=True)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MostPopular',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('article_list', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'most popular',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(max_length=200, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('introduction', models.TextField(help_text='Use unfiltered HTML. If this is not blank, the default template does not render any other fields before the article list.', blank=True)),
                ('icon', filebrowser.fields.FileBrowseField(max_length=200, verbose_name='Image', null=True, blank=True)),
                ('template', models.CharField(max_length=200, default='newsroom/topic_detail.html')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserEdit',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('edit_time', models.DateTimeField(auto_now=True)),
                ('article', models.ForeignKey(to='newsroom.Article')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['article__published', 'edit_time'],
            },
        ),
        migrations.AddField(
            model_name='article',
            name='author_01',
            field=models.ForeignKey(related_name='author_01', blank=True, to='newsroom.Author', verbose_name='first author', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='author_02',
            field=models.ForeignKey(related_name='author_02', blank=True, to='newsroom.Author', verbose_name='second author', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='author_03',
            field=models.ForeignKey(related_name='author_03', blank=True, to='newsroom.Author', verbose_name='third author', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='author_04',
            field=models.ForeignKey(related_name='author_04', blank=True, to='newsroom.Author', verbose_name='fourth author', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='author_05',
            field=models.ForeignKey(related_name='author_05', blank=True, to='newsroom.Author', verbose_name='fifth author', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(default=4, to='newsroom.Category'),
        ),
        migrations.AddField(
            model_name='article',
            name='main_topic',
            field=models.ForeignKey(related_name='main', blank=True, help_text="Used for generating'See also' list of articles.", to='newsroom.Topic', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='region',
            field=models.ForeignKey(blank=True, to='newsroom.Region', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='topics',
            field=models.ManyToManyField(to='newsroom.Topic', blank=True),
        ),
        migrations.AddField(
            model_name='article',
            name='user',
            field=models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='useredit',
            unique_together=set([('article', 'user')]),
        ),
    ]
