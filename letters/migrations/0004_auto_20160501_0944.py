# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('letters', '0003_auto_20160430_1852'),
    ]

    operations = [
        migrations.RenameField(
            model_name='letter',
            old_name='notified',
            new_name='notified_editors',
        ),
        migrations.AddField(
            model_name='letter',
            name='notified_letter_writer',
            field=models.BooleanField(default=False),
        ),
    ]
