# Generated by Django 3.2.15 on 2023-06-06 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('donationPage', '0004_auto_20230426_1121'),
    ]

    operations = [
        migrations.RenameField(
            model_name='donation',
            old_name='donation_amount',
            new_name='amount',
        ),
        migrations.RenameField(
            model_name='donation',
            old_name='donation_date',
            new_name='datetime_of_donation',
        ),
        migrations.RenameField(
            model_name='donation',
            old_name='recurring',
            new_name='notified',
        ),
        migrations.RenameField(
            model_name='donor',
            old_name='donor_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='donation',
            name='donation_slug',
        ),
        migrations.RemoveField(
            model_name='donation',
            name='verified',
        ),
        migrations.RemoveField(
            model_name='donor',
            name='registered_id',
        ),
        migrations.AddField(
            model_name='donation',
            name='section18a_issued',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='donation',
            name='certificate_issued',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='donation',
            name='currency_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='donationPage.currency'),
        ),
        migrations.AlterField(
            model_name='donation',
            name='platform',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='donor',
            name='donor_url',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.DeleteModel(
            name='Platform',
        ),
    ]
