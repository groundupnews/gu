# Generated by Django 3.2.15 on 2023-06-06 09:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donationPage', '0005_auto_20230606_1046'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donation',
            name='certificate_issued',
        ),
        migrations.RemoveField(
            model_name='donation',
            name='platform',
        ),
    ]