# Generated by Django 3.2.16 on 2023-01-23 01:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_salesname_valid'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrdersWithNoProject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endCustomer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.finalcustomers')),
                ('mainCustomer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.maincustomers')),
                ('rfp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.product')),
            ],
        ),
        migrations.CreateModel(
            name='MissingOrders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='project.project')),
            ],
        ),
    ]