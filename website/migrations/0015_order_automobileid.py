# Generated by Django 3.0.5 on 2020-08-04 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0014_auto_20200802_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='automobileId',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
