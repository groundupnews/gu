# Generated by Django 3.2.15 on 2023-05-31 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judgment', '0002_auto_20230520_1726'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='unique_id',
        ),
        migrations.AlterField(
            model_name='event',
            name='case_number',
            field=models.CharField(help_text='Please enter a valid South African court case number.', max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='email_address',
            field=models.EmailField(help_text='We may need to contact you but we will not share\nyour email address with anyone else.', max_length=254, verbose_name='Your email address'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_date',
            field=models.DateField(blank=True, help_text="Please give the exact date.\nIf you're not certain, please indicate in the notes below.", null=True, verbose_name='Date it happened'),
        ),
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.CharField(choices=[('R', 'Judgment reserved'), ('H', 'Judgment handed down'), ('S', 'Case settled'), ('O', 'Other')], help_text='Indicate if judgment was reserved, handed down or something else happened.', max_length=3, verbose_name='What happened'),
        ),
        migrations.AlterField(
            model_name='event',
            name='judges',
            field=models.TextField(blank=True, help_text='Enter first and surnames of judges, one per line.\nPlease enter at least one judge.', max_length=1000, verbose_name='Judge(s)'),
        ),
        migrations.AlterField(
            model_name='event',
            name='notes',
            field=models.TextField(blank=True, help_text='Use this to provide further information', max_length=2000),
        ),
    ]
