# Generated by Django 3.0.14 on 2021-04-27 08:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0026_auto_20210421_2258'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='commission',
            options={'ordering': ['invoice', 'created'], 'verbose_name': 'payment item'},
        ),
    ]