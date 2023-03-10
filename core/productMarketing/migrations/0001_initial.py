# Generated by Django 3.2.16 on 2023-01-20 14:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Currencies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.CharField(blank=True, choices=[('EUR', 'EUR'), ('USD', 'USD'), ('JPY', 'JPY'), ('MXN', 'MXN'), ('CHF', 'CHF')], max_length=3, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Dragon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transferDate', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('TRANSACTION_NUMBER', models.IntegerField(blank=True, default=-1, null=True)),
                ('OPPORTUNITY_DESCRIPTION', models.CharField(blank=True, default='fieldMissing', max_length=100, null=True)),
                ('CUSTOMER_CLASSIFICATION', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('END_CUSTOMER', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DC_CHANNEL', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('MARKET_APP', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('FOCUS_PROJECT_FLAG', models.CharField(blank=True, default='fieldMissing', max_length=10, null=True)),
                ('OPPORTUNITY_CHANNEL', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DC_REGION_NAME', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('SOCKET_COMMENT', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('ITEM_NUMBER', models.IntegerField(blank=True, default=-1, null=True)),
                ('PL', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('HFG', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('RFP_SP_NAME', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('CY_PART_FAMILY', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('CY_PART_NAME', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('MAIN_CUSTOMER', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DC_CUSTOMER', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('PRODUCT_DESCRIPTION', models.CharField(blank=True, default='fieldMissing', max_length=100, null=True)),
                ('COMMENT_SALES_I', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('SOCKET_COMPETITOR', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('CREATION_DAY', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('PRODUCT_STATUS_AGGREGATED', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('PRODUCT_STATUS', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('SOCKET_STATUS', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DESIGN_WIN_CLAIM_STATUS', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('OPPORTUNITY_REASON', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DESIGN_LOSS_DAY', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('LOST_REASON_DESCRIPTION', models.CharField(blank=True, default='fieldMissing', max_length=100, null=True)),
                ('SALES_FLAG', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('IFX_RESPONSIBLE', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DESIGN_WIN_EXP_MONTH', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('RAMP_UP_MONTH', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('RAMP_DOWN_MONTH', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('TRAFFIC_LIGHT', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('TRAFFIC_LIGHT_COMMENT', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('APPROVER_1', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('APPROVER_2', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DW_APPR_FIN_YEAR', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DW_APPR_FIN_QUARTER', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DW_APPR_FIN_MONTH', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DW_APPR_FIN_DAY', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('BUSINESS_WIN_MONTH', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('MAIN_CUSTOMER_NUMBER', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('DW_POT_UW_USD', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=15, null=True)),
                ('DW_ACHIEVE_USD', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=15, null=True)),
                ('PLANNED_REV_UW_USD', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=15, null=True)),
                ('LIFETIME_REV_USD', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=15, null=True)),
                ('IFX_PRODUCT_QUANTITY', models.IntegerField(blank=True, default=-1, null=True)),
                ('Item_Internal_Device', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
                ('Product', models.CharField(blank=True, default='fieldMissing', max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ErrorTypesSalesOpportunities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('errorType', models.SmallIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VhkCy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cy2020', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2021', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2022', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2023', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2024', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2025', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2026', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2027', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2028', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2029', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2030', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2031', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2032', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2033', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2034', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2035', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2036', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2037', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2038', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2039', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2040', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2041', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2042', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2043', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2044', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2045', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2046', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2047', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2048', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2049', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('cy2050', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=8, null=True)),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('valid', models.BooleanField(blank=True, default=True, null=True)),
                ('RFP', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.product')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='productMarketing.currencies')),
            ],
        ),
        migrations.CreateModel(
            name='SalesOpportunitiesConflicts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluationDate', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('dragonOpportunity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='productMarketing.dragon')),
                ('errorType', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='productMarketing.errortypessalesopportunities')),
            ],
        ),
        migrations.CreateModel(
            name='SalesOpportunities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dragonId', models.IntegerField(default=1)),
                ('sop', models.SmallIntegerField()),
                ('status', models.IntegerField()),
                ('projectName', models.CharField(blank=True, max_length=50, null=True)),
                ('modReason', models.CharField(blank=True, max_length=50, null=True)),
                ('applicationDetail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='salesOpportunityApplicationDetail', to='project.applicationdetail')),
                ('applicationMain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='salesOpportunityApplicationMain', to='project.applicationmain')),
                ('assumedProject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='salesOpportunityAssumedProject', to='project.project')),
                ('dragonOpportunity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='productMarketing.dragon')),
                ('finalCustomer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='salesOpportunityFinalCustomer', to='project.finalcustomers')),
                ('mainCustomer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='salesOpportunityMainCustomer', to='project.maincustomers')),
                ('salesName', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='salesOpportunitySalesName', to='project.salesname')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectVolumePricesLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('modifiedDate', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('valid', models.BooleanField(blank=True, default=True, null=True)),
                ('calenderYear', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('quantityCustomerEstimation', models.IntegerField(blank=True, null=True)),
                ('volumeComment', models.CharField(max_length=60)),
                ('source', models.CharField(blank=True, choices=[('Estimation', 'estimation'), ('Customer Information', 'customerInformation'), ('Purchase Order', 'purchaseOrder')], max_length=30, null=True)),
                ('priceSource', models.CharField(blank=True, choices=[('VPA', 'vpaDb'), ('PRICING OFFICE', 'priceDb'), ('Manual Entry', 'man')], max_length=30, null=True)),
                ('priceComment', models.CharField(blank=True, default='', max_length=60, null=True)),
                ('currency', models.CharField(blank=True, default='EUR', max_length=3, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=15, null=True)),
                ('priceValidityUntil', models.IntegerField(blank=True, default=2025, null=True)),
                ('priceSourceComment', models.CharField(blank=True, max_length=100, null=True)),
                ('runTimestamp', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('modreason', models.CharField(blank=True, choices=[('customerVolumes', 'customerVolumes'), ('volumesModification', 'volumesModification'), ('volumesCreation', 'volumesCreation'), ('pricesModification', 'pricesModification'), ('pricesCreation', 'pricesCreation'), ('vhk', 'vhk'), ('keyFacts', 'keyFacts')], max_length=20, null=True)),
                ('vhkValue', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=15, null=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='projectvolumepriceslog', to='project.project')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectVolumePrices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('createdDate', models.DateTimeField(auto_now_add=True)),
                ('modifiedDate', models.DateTimeField(auto_now=True)),
                ('valid', models.BooleanField(blank=True, default=True, null=True)),
                ('calenderYear', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('quantityCustomerEstimation', models.IntegerField(default=0)),
                ('volumeComment', models.CharField(max_length=60)),
                ('source', models.CharField(blank=True, choices=[('Estimation', 'estimation'), ('Customer Information', 'customerInformation'), ('Purchase Order', 'purchaseOrder')], max_length=30, null=True)),
                ('priceSource', models.CharField(blank=True, choices=[('VPA', 'vpaDb'), ('PRICING OFFICE', 'priceDb'), ('Manual Entry', 'man')], max_length=30, null=True)),
                ('currency', models.CharField(blank=True, default='EUR', max_length=3, null=True)),
                ('price', models.DecimalField(decimal_places=6, default=0.0, max_digits=15)),
                ('priceValidityUntil', models.IntegerField(blank=True, default=2025, null=True)),
                ('priceSourceComment', models.CharField(blank=True, max_length=100, null=True)),
                ('vhkValue', models.DecimalField(blank=True, decimal_places=6, default=0.0, max_digits=15, null=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projectvolumeprices', to='project.project')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectVolumeMonthLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calenderYear', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('source', models.CharField(blank=True, choices=[('Estimation', 'estimation'), ('Customer Information', 'customerInformation'), ('Purchase Order', 'purchaseOrder')], max_length=30, null=True)),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('modifiedDate', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('valid', models.BooleanField(blank=True, default=True, null=True)),
                ('runTimestamp', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('modreason', models.CharField(blank=True, choices=[('customerVolumes', 'customerVolumes'), ('volumesModification', 'volumesModification'), ('volumesCreation', 'volumesCreation'), ('pricesModification', 'pricesModification'), ('pricesCreation', 'pricesCreation'), ('vhk', 'vhk'), ('keyFacts', 'keyFacts')], max_length=20, null=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.project')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectVolumeMonth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calenderYear', models.SmallIntegerField(blank=True, default=0, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('source', models.CharField(blank=True, choices=[('Estimation', 'estimation'), ('Customer Information', 'customerInformation'), ('Purchase Order', 'purchaseOrder')], max_length=30, null=True)),
                ('date', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('modifiedDate', models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, null=True)),
                ('valid', models.BooleanField(blank=True, default=True, null=True)),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.project')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectsToSalesOpportunitiesConflicts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluationDate', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('errorType', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='productMarketing.errortypessalesopportunities')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='project.project')),
                ('salesOpportunity', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='productMarketing.salesopportunities')),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('validFrom', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('validTo', models.DateTimeField(blank=True, null=True)),
                ('valid', models.BooleanField(blank=True, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=6, default=1.0, max_digits=15, null=True)),
                ('currency', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='productMarketing.currencies')),
            ],
        ),
        migrations.AddConstraint(
            model_name='projectvolumepriceslog',
            constraint=models.UniqueConstraint(fields=('runTimestamp', 'project', 'calenderYear'), name='unique_together_project_log'),
        ),
        migrations.AddConstraint(
            model_name='projectvolumemonthlog',
            constraint=models.UniqueConstraint(fields=('runTimestamp', 'calenderYear', 'month', 'project'), name='unique_together_project_month_log'),
        ),
    ]
