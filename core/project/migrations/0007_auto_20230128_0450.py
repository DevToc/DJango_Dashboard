# Generated by Django 3.2.16 on 2023-01-28 03:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_remove_applicationdetail_appline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='strategicbusinessunits',
            name='appMain',
        ),
        migrations.AddField(
            model_name='applicationmain',
            name='appLine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.applicationline'),
        ),
        migrations.AddField(
            model_name='applicationmain',
            name='sbu',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.strategicbusinessunits'),
        ),
    ]
