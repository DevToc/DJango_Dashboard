from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.deletion import CASCADE, PROTECT, SET_NULL
from django.utils.timezone import now
from core.project.models import (
    Project,
    Product,
    MainCustomers,
    FinalCustomers,
    SalesName,
    ApplicationDetail,
    ApplicationMain,
)
from core.project.models import (
    Project,
    Product,
    MainCustomers,
    FinalCustomers,
    SalesName,
    ApplicationDetail,
    ApplicationMain,
    marketerMetadata,
    Distributors,
    OEM,
    EMS,
    Tier1,
    VPACustomers,
)
from smart_selects.db_fields import ChainedForeignKey, ChainedManyToManyField
from django.db.models import UniqueConstraint

from django.db.models.query import QuerySet
from django_group_by import GroupByMixin

# getting used user model
User = get_user_model()


class ProjectVolumePrices(models.Model):

    ALLOWABLE_TYPES_VOLUME_SOURCE = (
        ("Estimation", "estimation"),
        ("Customer Information", "customerInformation"),
        ("Purchase Order", "purchaseOrder"),
    )

    ALLOWABLE_TYPES_PRICE_SOURCES = (
        ("VPA", "vpaDb"),
        ("PRICING OFFICE", "priceDb"),
        ("Manual Entry", "man"),
    )

    date = models.DateTimeField(default=now, editable=False, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    project = models.ForeignKey(
        Project,
        on_delete=CASCADE,
        null=True,
        blank=True,
        related_name="projectvolumeprices",
    )
    valid = models.BooleanField(default=True, blank=True, null=True)
    calenderYear = models.SmallIntegerField(default=0, blank=True, null=True)

    # volumes
    quantity = models.IntegerField(default=0)
    quantityCustomerEstimation = models.IntegerField(default=0)
    volumeComment = models.CharField(max_length=60)
    source = models.CharField(
        max_length=30, choices=ALLOWABLE_TYPES_VOLUME_SOURCE, blank=True, null=True
    )

    # prices
    priceSource = models.CharField(
        max_length=30, choices=ALLOWABLE_TYPES_PRICE_SOURCES, blank=True, null=True
    )
    # priceComment = models.CharField(max_length=60, blank=True, null=True, default="")
    currency = models.CharField(max_length=3, default="EUR", blank=True, null=True)
    price = models.DecimalField(default=0.0, max_digits=15, decimal_places=6)
    priceValidityUntil = models.IntegerField(default=2025, blank=True, null=True)
    priceSourceComment = models.CharField(max_length=100, blank=True, null=True)
    vhkValue = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=15, decimal_places=6
    )

    def __str__(self):
        return f"ID: {self.id} - QTY: {self.quantity} - PRICE: {self.price} - YR: {self.calenderYear}"


class ProjectVolumePricesLog(models.Model):

    ALLOWABLE_TYPES_VOLUME_SOURCE = (
        ("Estimation", "estimation"),
        ("Customer Information", "customerInformation"),
        ("Purchase Order", "purchaseOrder"),
    )

    ALLOWABLE_TYPES_PRICE_SOURCES = (
        ("VPA", "vpaDb"),
        ("PRICING OFFICE", "priceDb"),
        ("Manual Entry", "man"),
    )

    ALLOWABLE_TYPES_MODIFCATIONS = (
        ("customerVolumes", "customerVolumes"),
        ("volumesModification", "volumesModification"),
        ("volumesCreation", "volumesCreation"),
        ("pricesModification", "pricesModification"),
        ("pricesCreation", "pricesCreation"),
        ("vhk", "vhk"),
        ("keyFacts", "keyFacts"),
    )

    date = models.DateTimeField(default=now, editable=False, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    modifiedDate = models.DateTimeField(
        default=now, editable=False, blank=True, null=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="projectvolumepriceslog",
    )
    valid = models.BooleanField(default=True, blank=True, null=True)
    calenderYear = models.SmallIntegerField(default=0, blank=True, null=True)

    # volumes
    quantity = models.IntegerField(blank=True, null=True)
    quantityCustomerEstimation = models.IntegerField(blank=True, null=True)
    volumeComment = models.CharField(max_length=60)
    source = models.CharField(
        max_length=30, choices=ALLOWABLE_TYPES_VOLUME_SOURCE, blank=True, null=True
    )

    # prices
    priceSource = models.CharField(
        max_length=30, choices=ALLOWABLE_TYPES_PRICE_SOURCES, blank=True, null=True
    )
    priceComment = models.CharField(max_length=60, blank=True, null=True, default="")
    currency = models.CharField(max_length=3, default="EUR", blank=True, null=True)
    price = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=15, decimal_places=6
    )
    vhkValue = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=15, decimal_places=6
    )

    priceValidityUntil = models.IntegerField(default=2025, blank=True, null=True)
    priceSourceComment = models.CharField(max_length=100, blank=True, null=True)
    # other
    runTimestamp = models.DateTimeField(
        default=now, editable=False, blank=True, null=True
    )
    modreason = models.CharField(
        max_length=20, choices=ALLOWABLE_TYPES_MODIFCATIONS, blank=True, null=True
    )
    vhkValue = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=15, decimal_places=6
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["runTimestamp", "project", "calenderYear"],
                name="unique_together_project_log",
            ),
        ]


class ProjectVolumeMonthQuerySet(QuerySet, GroupByMixin):
    pass


class ProjectVolumeMonth(models.Model):
    objects = ProjectVolumeMonthQuerySet.as_manager()

    ALLOWABLE_TYPES_VOLUME_SOURCE = (
        ("Estimation", "estimation"),
        ("Customer Information", "customerInformation"),
        ("Purchase Order", "purchaseOrder"),
    )
    calenderYear = models.SmallIntegerField(default=0, blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    source = models.CharField(
        max_length=30, choices=ALLOWABLE_TYPES_VOLUME_SOURCE, blank=True, null=True
    )
    date = models.DateTimeField(default=now, editable=False, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    modifiedDate = models.DateTimeField(
        default=now, editable=False, blank=True, null=True
    )
    project = models.ForeignKey(Project, on_delete=CASCADE, null=True, blank=True)
    valid = models.BooleanField(default=True, blank=True, null=True)
    # fiscal year and quarter
    fiscal_year = models.PositiveSmallIntegerField(null=True, blank=True)
    fiscal_quarter = models.PositiveSmallIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculate the fiscal year based on the month
        if self.month >= 10:
            self.fiscal_year = self.calenderYear + 1
        else:
            self.fiscal_year = self.calenderYear

        # Calculate the fiscal quarter based on the month
        if self.month in [10, 11, 12]:
            self.fiscal_quarter = 1
        elif self.month in [1, 2, 3]:
            self.fiscal_quarter = 2
        elif self.month in [4, 5, 6]:
            self.fiscal_quarter = 3
        else:
            self.fiscal_quarter = 4
        return super().save(*args, **kwargs)


class ProjectVolumeMonthLog(models.Model):
    ALLOWABLE_TYPES_MODIFCATIONS = (
        ("customerVolumes", "customerVolumes"),
        ("volumesModification", "volumesModification"),
        ("volumesCreation", "volumesCreation"),
        ("pricesModification", "pricesModification"),
        ("pricesCreation", "pricesCreation"),
        ("vhk", "vhk"),
        ("keyFacts", "keyFacts"),
    )

    ALLOWABLE_TYPES_VOLUME_SOURCE = (
        ("Estimation", "estimation"),
        ("Customer Information", "customerInformation"),
        ("Purchase Order", "purchaseOrder"),
    )
    calenderYear = models.SmallIntegerField(default=0, blank=True, null=True)
    month = models.IntegerField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    source = models.CharField(
        max_length=30, choices=ALLOWABLE_TYPES_VOLUME_SOURCE, blank=True, null=True
    )
    date = models.DateTimeField(default=now, editable=False, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    modifiedDate = models.DateTimeField(
        default=now, editable=False, blank=True, null=True
    )
    project = models.ForeignKey(Project, on_delete=SET_NULL, null=True, blank=True)
    valid = models.BooleanField(default=True, blank=True, null=True)
    runTimestamp = models.DateTimeField(
        default=now, editable=False, blank=True, null=True
    )
    modreason = models.CharField(
        max_length=20, choices=ALLOWABLE_TYPES_MODIFCATIONS, blank=True, null=True
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    "runTimestamp",
                    "calenderYear",
                    "month",
                    "project",
                ],
                name="unique_together_project_month_log",
            ),
        ]

"""
it is understood as the excahnge rate from source into EUR
starting March 23 this is only an archive... written by a Django signal when django_currencies.Currency is modified or created
"""
class CurrenciesArchive(models.Model):
    ALLOWABLE_TYPES_CURRENCIES = (
        ("EUR", "EUR"),
        ("USD", "USD"),
        ("JPY", "JPY"),
        ("MXN", "MXN"),
        ("CHF", "CHF"),
    )
    currency = models.CharField(
        max_length=3, choices=ALLOWABLE_TYPES_CURRENCIES, blank=True, null=True
    )


class ExchangeRatesArchive(models.Model):

    ALLOWABLE_TYPES_CURRENCIES = (
        ("EUR", "EUR"),
        ("USD", "USD"),
        ("JPY", "JPY"),
        ("MXN", "MXN"),
        ("CHF", "CHF"),
    )

    # tbd month, year, day, validty, directionality
    date = models.DateTimeField(default=now, editable=False)
    currency = models.ForeignKey(CurrenciesArchive, on_delete=models.CASCADE, default=1)
    validFrom = models.DateTimeField(default=now, editable=True, blank=True, null=True)
    validTo = models.DateTimeField(editable=True, blank=True, null=True)
    valid = models.BooleanField(blank=True, null=True)
    rate = models.DecimalField(
        default=1.0, blank=True, null=True, max_digits=15, decimal_places=6
    )


class VhkCy(models.Model):
    from currencies.models import Currency

    RFP = models.ForeignKey(Product, on_delete=models.CASCADE)
    # calendarYear = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    cy2020 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2021 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2022 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2023 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2024 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2025 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2026 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2027 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2028 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2029 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2030 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2031 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2032 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2033 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2034 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2035 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2036 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2037 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2038 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2039 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2040 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2041 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2042 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2043 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2044 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2045 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2046 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2047 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2048 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2049 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    cy2050 = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=8, decimal_places=6
    )
    date = models.DateTimeField(default=now, editable=False, blank=True, null=True)
    valid = models.BooleanField(default=True, blank=True, null=True)


####
class Dragon(models.Model):
    transferDate = models.DateTimeField(default=now, editable=False)
    TRANSACTION_NUMBER = models.IntegerField(default=-1, blank=True, null=True)
    OPPORTUNITY_DESCRIPTION = models.CharField(
        max_length=100, default="fieldMissing", blank=True, null=True
    )
    CUSTOMER_CLASSIFICATION = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    # models.ForeignKey(FinalCustomers, on_delete=models.PROTECT, blank=True, null=True)
    END_CUSTOMER = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DC_CHANNEL = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    MARKET_APP = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    FOCUS_PROJECT_FLAG = models.CharField(
        max_length=10, default="fieldMissing", blank=True, null=True
    )
    OPPORTUNITY_CHANNEL = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DC_REGION_NAME = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    SOCKET_COMMENT = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    ITEM_NUMBER = models.IntegerField(default=-1, blank=True, null=True)
    PL = models.CharField(max_length=30, default="fieldMissing", blank=True, null=True)
    HFG = models.CharField(max_length=30, default="fieldMissing", blank=True, null=True)
    RFP_SP_NAME = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    CY_PART_FAMILY = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    CY_PART_NAME = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    # models.ForeignKey(MainCustomers, on_delete=models.CASCADE, blank=True, null=True )
    MAIN_CUSTOMER = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DC_CUSTOMER = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    PRODUCT_DESCRIPTION = models.CharField(
        max_length=100, default="fieldMissing", blank=True, null=True
    )
    COMMENT_SALES_I = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    SOCKET_COMPETITOR = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    CREATION_DAY = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    PRODUCT_STATUS_AGGREGATED = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    PRODUCT_STATUS = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    SOCKET_STATUS = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DESIGN_WIN_CLAIM_STATUS = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    OPPORTUNITY_REASON = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DESIGN_LOSS_DAY = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    LOST_REASON_DESCRIPTION = models.CharField(
        max_length=100, default="fieldMissing", blank=True, null=True
    )
    SALES_FLAG = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    IFX_RESPONSIBLE = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DESIGN_WIN_EXP_MONTH = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    RAMP_UP_MONTH = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    RAMP_DOWN_MONTH = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    TRAFFIC_LIGHT = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    TRAFFIC_LIGHT_COMMENT = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    APPROVER_1 = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    APPROVER_2 = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DW_APPR_FIN_YEAR = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DW_APPR_FIN_QUARTER = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DW_APPR_FIN_MONTH = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DW_APPR_FIN_DAY = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    BUSINESS_WIN_MONTH = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    MAIN_CUSTOMER_NUMBER = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    DW_POT_UW_USD = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=15, decimal_places=2
    )
    DW_ACHIEVE_USD = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=15, decimal_places=2
    )
    PLANNED_REV_UW_USD = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=15, decimal_places=2
    )
    LIFETIME_REV_USD = models.DecimalField(
        default=0.0, blank=True, null=True, max_digits=15, decimal_places=2
    )
    IFX_PRODUCT_QUANTITY = models.IntegerField(default=-1, blank=True, null=True)
    Item_Internal_Device = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )
    Product = models.CharField(
        max_length=30, default="fieldMissing", blank=True, null=True
    )


class SalesOpportunities(models.Model):
    # functional key
    mainCustomer = models.ForeignKey(
        MainCustomers,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="salesOpportunityMainCustomer",
    )
    finalCustomer = models.ForeignKey(
        FinalCustomers,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="salesOpportunityFinalCustomer",
    )
    salesName = models.ForeignKey(
        SalesName,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="salesOpportunitySalesName",
    )

    # blablbabla
    dragonOpportunity = models.ForeignKey(
        Dragon, on_delete=PROTECT, null=True, blank=True
    )

    dragonId = models.IntegerField(default=1)
    applicationMain = models.ForeignKey(
        ApplicationMain,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="salesOpportunityApplicationMain",
    )
    applicationDetail = models.ForeignKey(
        ApplicationDetail,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="salesOpportunityApplicationDetail",
    )
    assumedProject = models.ForeignKey(
        Project,
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="salesOpportunityAssumedProject",
    )
    sop = models.SmallIntegerField()
    status = models.IntegerField()
    projectName = models.CharField(max_length=50, blank=True, null=True)
    modReason = models.CharField(max_length=50, blank=True, null=True)


class ErrorTypesSalesOpportunities(models.Model):
    errorType = models.SmallIntegerField(blank=True, null=True)
    errorDescription = models.CharField(max_length=35, blank=True, null=True)


#    evaluationDate = models.DateTimeField(default=now, editable=False)


class SalesOpportunitiesConflicts(models.Model):
    dragonOpportunity = models.ForeignKey(
        Dragon, on_delete=CASCADE, null=True, blank=True
    )
    errorType = models.ForeignKey(
        ErrorTypesSalesOpportunities, on_delete=PROTECT, null=True, blank=True
    )
    evaluationDate = models.DateTimeField(default=now, editable=False)


class ProjectsToSalesOpportunitiesConflicts(models.Model):
    errorType = models.ForeignKey(
        ErrorTypesSalesOpportunities, on_delete=PROTECT, null=True, blank=True
    )
    salesOpportunity = models.ForeignKey(
        SalesOpportunities, on_delete=CASCADE, null=True, blank=True
    )
    project = models.ForeignKey(Project, on_delete=CASCADE, null=True, blank=True)
    evaluationDate = models.DateTimeField(default=now, editable=False)
