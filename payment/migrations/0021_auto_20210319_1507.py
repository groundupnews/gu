# Generated by Django 3.0.10 on 2021-03-19 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0020_invoice_additional_emails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
