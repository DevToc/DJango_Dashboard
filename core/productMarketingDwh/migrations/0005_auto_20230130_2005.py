# Generated by Django 3.2.16 on 2023-01-30 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productMarketingDwh', '0004_auto_20230123_1756'),
    ]

    operations = [
        migrations.AddField(
            model_name='boup',
            name='vhkDate',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='boup',
            name='fxRate',
            field=models.DecimalField(blank=True, decimal_places=5, max_digits=10, null=True),
        ),
    ]