# Generated by Django 2.1.7 on 2019-04-24 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('newsroom', '0005_auto_20190424_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='freelancer',
            field=models.CharField(choices=[('n', 'No'), ('f', 'Freelancer'), ('c', 'Commissioned staff')], default='n', max_length=1),
        ),
    ]
