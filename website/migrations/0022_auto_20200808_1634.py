# Generated by Django 3.0.5 on 2020-08-08 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0021_auto_20200808_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='carModel',
            field=models.CharField(max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.CharField(max_length=70, null=True),
        ),
    ]
