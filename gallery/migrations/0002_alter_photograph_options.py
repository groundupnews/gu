# Generated by Django 4.2.18 on 2025-02-05 08:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='photograph',
            options={'ordering': ['-featured', '-date_taken', '-modified']},
        ),
    ]
