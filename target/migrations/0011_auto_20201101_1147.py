# Generated by Django 3.0.10 on 2020-11-01 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('target', '0010_auto_20201101_1127'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='tweet_notified_published',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='target',
            name='tweet_notified_solution',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='target',
            name='publish_solution_after',
            field=models.SmallIntegerField(default=24, help_text='Make solution available after this many hours', null=True, verbose_name='solution time'),
        ),
    ]
