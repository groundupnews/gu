# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0002_auto_20160430_1636'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='letter',
            options={'ordering': ['article', 'position', 'published']},
        ),
        migrations.AddField(
            model_name='letter',
            name='notified',
            field=models.BooleanField(default=False),
        ),
    ]
