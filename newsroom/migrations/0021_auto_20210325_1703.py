# Generated by Django 3.0.10 on 2021-03-25 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0020_auto_20210323_1550'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='correction',
            options={'ordering': ['-created']},
        ),
    ]
