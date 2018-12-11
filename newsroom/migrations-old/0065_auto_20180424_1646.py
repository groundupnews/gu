# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-24 14:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0064_auto_20180424_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='copyright',
            field=models.TextField(blank=True, default='<p>&copy; 2018 GroundUp.<a rel="license"   href="http://creativecommons.org/licenses/by-nd/4.0/">    <svg viewBox="0 0 100 100"         class="icon icon-creative-commons">        <use xlink:href="#icon-creative-commons">        </use>    </svg></a><br />This article is licensed under a <a rel="license"   href="http://creativecommons.org/licenses/by-nd/4.0/">Creative Commons Attribution-NoDerivatives 4.0 International License</a>.</p><p>You may republish this article, so long as you credit the authors and GroundUp, and do not change the text. Please include a link back to the original article.</p>'),
        ),
    ]