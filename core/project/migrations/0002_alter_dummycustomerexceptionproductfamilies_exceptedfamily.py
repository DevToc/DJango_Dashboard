# Generated by Django 3.2.16 on 2023-01-20 23:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dummycustomerexceptionproductfamilies',
            name='exceptedFamily',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]