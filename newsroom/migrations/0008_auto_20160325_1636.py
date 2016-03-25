# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0007_article_encourage_republish'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='copyright',
            field=models.TextField(blank=True, default='&copy; 2016 GroundUp. <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nd/4.0/80x15.png" /></a><br />This article is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nd/4.0/">Creative Commons Attribution-NoDerivatives 4.0 International License</a>.<p>You may republish this article, so long as you credit the authors and GroundUp, and do not change the text. Please include a link back to the original article.</p>'),
        ),
    ]
