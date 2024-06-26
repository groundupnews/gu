# Generated by Django 3.2.6 on 2022-01-10 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0024_author_allowance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='copyright',
            field=models.TextField(blank=True, default='<p>&copy; 2022 GroundUp. This article is licensed under a <a rel="license"   href="http://creativecommons.org/licenses/by-nd/4.0/">Creative Commons Attribution-NoDerivatives 4.0 International License</a>.</p><p>You may republish this article, so long as you credit the authors and GroundUp, and do not change the text. Please include a link back to the original article.</p><p>We put an invisible pixel in the article so that we can count traffic to republishers. All analytics tools are solely on our servers. We do not give our logs to any third party. Logs are deleted after two weeks. We do not use any IP address identifying information except to count regional traffic. We are solely interested in counting hits, <b>not tracking</b> users. If you republish, please do not delete the invisible pixel.</p>'),
        ),
    ]
