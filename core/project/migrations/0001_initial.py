# Generated by Django 3.2.16 on 2023-01-20 14:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appDetailDescription', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ApplicationLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicationLineShortName', models.CharField(max_length=10)),
                ('applicationLineLongName', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='ApplicationMain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appMainDescription', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DistributionChannels',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dcChannel', models.CharField(blank=True, max_length=12, null=True)),
                ('dcChannelDescription', models.CharField(blank=True, max_length=12, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Distributors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distributorName', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('emsName', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FinalCustomers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finalCustomerName', models.CharField(blank=True, max_length=40, null=True)),
                ('valid', models.BooleanField(blank=True, default=False, null=True)),
                ('dummy', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LegalEntities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leShortName', models.CharField(max_length=5)),
                ('leLongName', models.CharField(max_length=35)),
            ],
        ),
        migrations.CreateModel(
            name='MainCustomers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customerName', models.CharField(blank=True, max_length=40, null=True)),
                ('valid', models.BooleanField(blank=True, default=False, null=True)),
                ('dummy', models.BooleanField(blank=True, default=False, null=True)),
                ('finalCustomers', models.ManyToManyField(to='project.FinalCustomers')),
            ],
        ),
        migrations.CreateModel(
            name='marketerMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=40, null=True)),
                ('familyName', models.CharField(blank=True, max_length=40, null=True)),
                ('country', models.CharField(blank=True, max_length=15, null=True)),
                ('applicationLine', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.applicationline')),
                ('legalEntity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.legalentities')),
                ('user', models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OEM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oemName', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PriceStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priceType', models.CharField(blank=True, max_length=5, null=True)),
                ('priceTypeDisplay', models.CharField(blank=True, max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hfg', models.CharField(blank=True, max_length=20, null=True)),
                ('ppos', models.CharField(blank=True, max_length=30, null=True)),
                ('rfp', models.CharField(blank=True, max_length=40, null=True)),
                ('basicType', models.CharField(blank=True, max_length=40, null=True)),
                ('availablePGS', models.CharField(blank=True, default=True, max_length=40, null=True)),
                ('valid', models.BooleanField(blank=True, default=False, null=True)),
                ('dummy', models.BooleanField(blank=True, default=False, null=True)),
                ('familyHelper', models.CharField(blank=True, max_length=30, null=True)),
                ('familyDetailHelper', models.CharField(blank=True, max_length=30, null=True)),
                ('seriesHelper', models.CharField(blank=True, max_length=30, null=True)),
                ('packageHelper', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductFamily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('family_name', models.CharField(max_length=200)),
                ('valid', models.BooleanField(blank=True, default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spNumber', models.IntegerField(blank=True, null=True)),
                ('familyPriceApplicable', models.BooleanField(blank=True, default=False, null=True)),
                ('familyPriceDetails', models.CharField(blank=True, max_length=50, null=True)),
                ('otherPriceComments', models.CharField(blank=True, max_length=50, null=True)),
                ('modifiedDate', models.DateTimeField(auto_now=True)),
                ('creationDate', models.DateTimeField(auto_now_add=True)),
                ('estimatedSop', models.IntegerField(blank=True, default=2020, null=True, validators=[django.core.validators.MinValueValidator(2020), django.core.validators.MaxValueValidator(2050)], verbose_name='Estimated SOP')),
                ('valid', models.BooleanField(blank=True, default=True, null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('projectName', models.CharField(max_length=150, verbose_name='Project Name')),
                ('projectDescription', models.CharField(blank=True, default='', max_length=400, null=True)),
                ('draft', models.BooleanField(default=True)),
                ('priceValidUntil', models.DateField(blank=True, null=True)),
                ('salesContact', models.CharField(blank=True, max_length=30, null=True)),
                ('is_viewing', models.BooleanField(default=False, help_text='Checks if someone is viewing this project')),
                ('dummy', models.BooleanField(default=False)),
                ('projectReviewed', models.BooleanField(blank=True, default=False, null=True)),
                ('reviewDate', models.DateField(blank=True, null=True)),
                ('modreason', models.CharField(blank=True, max_length=15, null=True)),
                ('applicationDetail', smart_selects.db_fields.ChainedForeignKey(auto_choose=True, chained_field='applicationMain', chained_model_field='appMain', null=True, on_delete=django.db.models.deletion.CASCADE, to='project.applicationdetail', verbose_name='Application Detail')),
                ('applicationMain', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='project.applicationmain', verbose_name='Application Main')),
                ('dcChannel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.distributionchannels')),
                ('distributor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.distributors')),
                ('ems', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.ems', verbose_name='EMS')),
                ('finalCustomer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='project.finalcustomers', verbose_name='Final Customer')),
                ('is_viewing_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='is_viewing_user', to=settings.AUTH_USER_MODEL)),
                ('mainCustomer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='project.maincustomers', verbose_name='Main Customer')),
                ('oem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.oem', verbose_name='OEM')),
                ('priceType', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.pricestatus')),
                ('productMarketer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='project.marketermetadata', verbose_name='Product Marketer')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default=0, max_length=15)),
                ('statusDisplay', models.CharField(blank=True, max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Regions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(default='EMEA', max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='SalesContacts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=40, null=True)),
                ('deptarment', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SecondRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secondRegion', models.CharField(blank=True, max_length=10, null=True, verbose_name='Second Region')),
            ],
        ),
        migrations.CreateModel(
            name='Tier1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tierOneName', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VPACustomers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customerName', models.CharField(blank=True, max_length=40, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalesName',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('dummy', models.BooleanField(blank=True, default=False, null=True)),
                ('rfp', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='project.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectError',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('error_ids', models.CharField(max_length=100)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='project.project')),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.regions'),
        ),
        migrations.AddField(
            model_name='project',
            name='sales_name',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.salesname'),
        ),
        migrations.AddField(
            model_name='project',
            name='secondRegion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.secondregion'),
        ),
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.projectstatus'),
        ),
        migrations.AddField(
            model_name='project',
            name='tier1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.tier1', verbose_name='Tier 1'),
        ),
        migrations.AddField(
            model_name='project',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='vpaCustomer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.vpacustomers', verbose_name='OEM'),
        ),
        migrations.CreateModel(
            name='ProductSeries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('series', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=40, null=True)),
                ('valid', models.BooleanField(blank=True, default=False, null=True)),
                ('dummy', models.BooleanField(blank=True, default=False, null=True)),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.productfamily')),
            ],
        ),
        migrations.CreateModel(
            name='ProductPackage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('package', models.CharField(max_length=200)),
                ('description', models.CharField(blank=True, max_length=40, null=True)),
                ('valid', models.BooleanField(blank=True, default=False, null=True)),
                ('dummy', models.BooleanField(blank=True, default=False, null=True)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.productseries')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='package',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.productpackage'),
        ),
        migrations.CreateModel(
            name='DummyCustomerExceptionProductFamilies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exceptedFamily', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.productfamily')),
            ],
        ),
        migrations.AddField(
            model_name='applicationdetail',
            name='appMain',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.applicationmain'),
        ),
        migrations.AddField(
            model_name='project',
            name='syntheticProjectName',
            field=models.CharField(blank=True, max_length=65, null=True, verbose_name='SyntheticProjectName'),
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('mainCustomer', 'finalCustomer', 'draft', 'productMarketer', 'applicationDetail', 'applicationMain', 'sales_name', 'dummy', 'syntheticProjectName'), name='unique_together_project'),
        ),
    ]
