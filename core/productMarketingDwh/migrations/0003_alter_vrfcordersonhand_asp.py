# Generated by Django 3.2.16 on 2023-01-22 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productMarketingDwh', '0002_auto_20230122_0149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vrfcordersonhand',
            name='asp',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=16, null=True),
        ),
    ]
