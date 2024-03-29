# Generated by Django 3.2.15 on 2023-03-22 09:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Donor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('donor_name', models.CharField(max_length=200)),
                ('display_name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200)),
                ('registered_id', models.CharField(max_length=15)),
                ('donor_url', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('donation_date', models.DateTimeField(blank=True, null=True)),
                ('recurring', models.BooleanField(default=False)),
                ('donation_amount', models.PositiveIntegerField(default=0)),
                ('currency_type', models.CharField(max_length=4)),
                ('certificate_issued', models.BooleanField(default=False)),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='donationPage.donor')),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='donationPage.platform')),
            ],
        ),
    ]
