# Generated by Django 3.2.16 on 2023-01-27 23:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_missingorders_orderswithnoproject'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationdetail',
            name='appLine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.applicationline'),
        ),
        migrations.AlterField(
            model_name='project',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.projectstatus'),
        ),
        migrations.CreateModel(
            name='StrategicBusinessUnits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('businessUnitName', models.CharField(blank=True, max_length=40, null=True)),
                ('appMain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.applicationmain')),
            ],
        ),
    ]
