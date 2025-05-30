# Generated by Django 3.2.13 on 2022-07-03 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0031_correction_publishers_notified'),
    ]

    operations = [
        migrations.CreateModel(
            name='WetellBulletin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.PositiveIntegerField()),
                ('published', models.DateTimeField()),
                ('data', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-published'],
            },
        ),
        migrations.AddConstraint(
            model_name='wetellbulletin',
            constraint=models.UniqueConstraint(fields=('service', 'published'), name='service_published'),
        ),
    ]
