# Generated by Django 3.2.16 on 2023-01-23 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productMarketingDwh', '0003_alter_vrfcordersonhand_asp'),
    ]

    operations = [
        migrations.AddField(
            model_name='vrfcsalesforecast',
            name='fiscalQuarter',
            field=models.SmallIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='vrfcsalesforecast',
            name='year',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
