# Generated by Django 3.2.16 on 2023-02-10 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0011_auto_20230208_0045'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='contractualCurrency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
