# Generated by Django 3.2.16 on 2023-02-23 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0013_auto_20230214_0332'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='plHfg',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]