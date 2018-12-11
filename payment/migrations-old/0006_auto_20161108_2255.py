# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-11-08 20:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_auto_20161108_0659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='address',
            field=models.TextField(blank=True, help_text='Required by SARS'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='dob',
            field=models.DateField(blank=True, help_text='Required by SARS', null=True, verbose_name='date of birth'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='tax_percent',
            field=models.DecimalField(decimal_places=0, default=25, help_text='Unless you have a tax directive we have to deduct 25% PAYE', max_digits=2, verbose_name='PAYE %'),
        ),
    ]