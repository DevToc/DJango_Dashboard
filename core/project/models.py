from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from smart_selects.db_fields import ChainedForeignKey
from django.db.models import UniqueConstraint

# Create your models here.

# getting used user model
User = get_user_model()


class ApplicationLine(models.Model):
    applicationLineShortName = models.CharField(max_length=40)
    applicationLineLongName = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.applicationLineShortName}"


class LegalEntities(models.Model):
    leShortName = models.CharField(max_length=5)
    leLongName = models.CharField(max_length=35)

    def __str__(self):
        return f"{self.leShortName} {self.leLongName}"


class marketerMetadata(models.Model):

    name = models.CharField(max_length=40, blank=True, null=True)
    familyName = models.CharField(max_length=40, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=1)
    country = models.CharField(max_length=15, blank=True, null=True)
    legalEntity = models.ForeignKey(
        LegalEntities, on_delete=models.PROTECT, blank=True, null=True
    )
    applicationLine = models.ForeignKey(
        ApplicationLine, on_delete=models.PROTECT, blank=True, null=True
    )  # default = "ATV.PSE"

    def __str__(self):
        return f"{self.name} {self.familyName}"


class StrategicBusinessUnits(models.Model):
    businessUnitName = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.businessUnitName


class ApplicationMain(models.Model):
    appMainDescription = models.CharField(max_length=40, blank=True, null=True)
    appLine = models.ForeignKey(
        ApplicationLine, on_delete=models.SET_NULL, blank=True, null=True
    )
    sbu = models.ForeignKey(
        StrategicBusinessUnits, on_delete=models.SET_NULL, blank=True, null=True
    )

    def __str__(self):
        return self.appMainDescription


class ApplicationDetail(models.Model):

    appDetailDescription = models.CharField(
        max_length=52, blank=True, null=True)
    appMain = models.ForeignKey(
        ApplicationMain, on_delete=models.PROTECT, blank=True, null=True
    )
    """
    appLine = models.ForeignKey(
        ApplicationLine, on_delete=models.SET_NULL, blank=True, null=True
    )
    """

    def __str__(self):
        return self.appDetailDescription


class FinalCustomers(models.Model):
    # relation removed upon agreement with customer on nov 25th
    """
    mainCust = models.ForeignKey(
        MainCustomers, on_delete=models.SET_NULL, null=True
    )
    """
    finalCustomerName = models.CharField(max_length=40, blank=True, null=True)
    valid = models.BooleanField(default=False, blank=True, null=True)
    dummy = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.finalCustomerName

    """
    class Meta:
        unique_together = ["mainCust", "finalCustomerName"]
    """


class MainCustomers(models.Model):
    customerName = models.CharField(max_length=40, blank=True, null=True)
    valid = models.BooleanField(default=False, blank=True, null=True)
    dummy = models.BooleanField(default=False, blank=True, null=True)
    finalCustomers = models.ManyToManyField(FinalCustomers)

    def __str__(self):
        return self.customerName


class ProductFamily(models.Model):
    family_name = models.CharField(max_length=200)
    valid = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.family_name


# product families in this list will be allowed to use a dummy customer


class DummyCustomerExceptionProductFamilies(models.Model):

    exceptedFamily = models.CharField(max_length=50, blank=True, null=True)
    """
    exceptedFamily = models.ForeignKey(
        ProductFamily, on_delete=models.PROTECT, blank=True, null=True
    )
    """


class ProductSeries(models.Model):
    family = models.ForeignKey(ProductFamily, on_delete=models.CASCADE)
    series = models.CharField(max_length=200)
    description = models.CharField(max_length=40, blank=True, null=True)
    valid = models.BooleanField(default=False, blank=True, null=True)
    dummy = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.series


class ProductPackage(models.Model):
    series = models.ForeignKey(ProductSeries, on_delete=models.CASCADE)
    package = models.CharField(max_length=200)
    description = models.CharField(max_length=40, blank=True, null=True)
    valid = models.BooleanField(default=False, blank=True, null=True)
    dummy = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        return self.package


class Product(models.Model):
    hfg = models.CharField(max_length=20, blank=True, null=True)
    ppos = models.CharField(max_length=30, blank=True, null=True)
    rfp = models.CharField(max_length=40, blank=True, null=True)
    package = models.ForeignKey(
        ProductPackage, on_delete=models.SET_NULL, null=True)
    basicType = models.CharField(max_length=40, blank=True, null=True)
    availablePGS = models.CharField(
        max_length=40, blank=True, null=True, default=True)
    valid = models.BooleanField(default=False, blank=True, null=True)
    dummy = models.BooleanField(default=False, blank=True, null=True)
    familyHelper = models.CharField(max_length=30, blank=True, null=True)
    familyDetailHelper = models.CharField(max_length=30, blank=True, null=True)
    seriesHelper = models.CharField(max_length=30, blank=True, null=True)
    packageHelper = models.CharField(max_length=30, blank=True, null=True)
    plHfg = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return f"{self.rfp}"


class SalesName(models.Model):
    rfp = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=40)
    dummy = models.BooleanField(default=False, blank=True, null=True)
    valid = models.BooleanField(default=True, blank=True, null=True)

    def __str__(self):
        return self.name


class Distributors(models.Model):
    distributorName = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.distributorName


class EMS(models.Model):
    emsName = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.emsName


class Tier1(models.Model):
    tierOneName = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.tierOneName


class OEM(models.Model):
    oemName = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.oemName


class VPACustomers(models.Model):
    customerName = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.customerName


class SalesContacts(models.Model):

    name = models.CharField(max_length=40, blank=True, null=True)
    deptarment = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.name


class ProjectStatus(models.Model):
    """
    ALLOWABLE_TYPES_PROJECT_STATUS = (
        ("100", "BW (100%)"),
        ("90", "DW (90%)"),
        ("60", "DI (60%)"),
        ("40", "DI (40%)"),
        ("10", "OP (10%)"),
        ("0", "LO (0%)"),
    )
    """

    status = models.CharField(max_length=15, default=0)
    statusDisplay = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.statusDisplay


class Regions(models.Model):
    """
    ALLOWABLE_TYPES_REGION = (
        ("EMEA", "EMEA"),
        ("AMERICAS", "AMERICAS"),
        ("AP", "AP"),
        ("JAPAN", "JAPAN"),
        ("GC", "GC"),
        ("DIVERSE", "DIVERSE"),
    )
    """

    region = models.CharField(max_length=10, default="EMEA")

    def __str__(self):
        return self.region


class SecondRegion(models.Model):
    secondRegion = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Second Region",
    )

    def __str__(self):
        return self.secondRegion


class DistributionChannels(models.Model):
    """
        ALLOWABLE_TYPES_DCCHANNEL = (
        ("direct", "Direct"),
        ("distribution", "Distribution"),
    )
    """

    dcChannel = models.CharField(max_length=12, blank=True, null=True)
    dcChannelDescription = models.CharField(
        max_length=12, blank=True, null=True)

    def __str__(self):
        return self.dcChannelDescription


class PriceStatus(models.Model):
    """
        ALLOWABLE_TYPES_PRICE_STATUS = (
        ("estim", "Estimation"),
        ("quote", "Quotation"),
        ("contr", "Contract"),
    )

    """

    priceType = models.CharField(max_length=5, blank=True, null=True)
    priceTypeDisplay = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.priceTypeDisplay


class Project(models.Model):

    ALLOWABLE_TYPES_PROJECT_STATUS = (
        ("100", "BW (100%)"),
        ("90", "DW (90%)"),
        ("60", "DI (60%)"),
        ("40", "DI (40%)"),
        ("10", "OP (10%)"),
        ("0", "LO (0%)"),
    )

    ALLOWABLE_TYPES_REGION = (
        ("EMEA", "EMEA"),
        ("AMERICAS", "AMERICAS"),
        ("AP", "AP"),
        ("JAPAN", "JAPAN"),
        ("GC", "GC"),
        ("MISC", "MISC"),
    )

    ALLOWABLE_TYPES_DCCHANNEL = (
        ("direct", "Direct"),
        ("distribution", "Distribution"),
    )

    ALLOWABLE_TYPES_PRICE_STATUS = (
        ("estim", "Estimation"),
        ("quote", "Quotation"),
        ("contr", "Contract"),
    )

    productMarketer = models.ForeignKey(
        marketerMetadata, on_delete=models.PROTECT, verbose_name="Product Marketer"
    )
    spNumber = models.IntegerField(blank=True, null=True)

    applicationLine = models.ForeignKey(
        ApplicationLine, on_delete=models.PROTECT, verbose_name="Application Line", blank=True, null=True
    )
    """
    applicationMain = models.ForeignKey(
        ApplicationMain, on_delete=models.PROTECT, verbose_name="Application Main"
    )
    """
    applicationMain = ChainedForeignKey(
        ApplicationMain,
        chained_field="applicationLine",
        chained_model_field="appLine",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
        null=True,
        verbose_name="Application Main",
    )

    applicationDetail = ChainedForeignKey(
        ApplicationDetail,
        chained_field="applicationMain",
        chained_model_field="appMain",
        show_all=False,
        auto_choose=True,
        sort=True,
        on_delete=models.PROTECT,
        null=True,
        verbose_name="Application Detail",
    )

    familyPriceApplicable = models.BooleanField(
        default=False, blank=True, null=True)
    familyPriceDetails = models.CharField(max_length=50, blank=True, null=True)
    otherPriceComments = models.CharField(max_length=50, blank=True, null=True)

    user = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True)
    modifiedDate = models.DateTimeField(auto_now=True)
    creationDate = models.DateTimeField(auto_now_add=True)

    estimatedSop = models.IntegerField(
        blank=True,
        null=True,
        default=2020,
        validators=[MinValueValidator(2020), MaxValueValidator(2050)],
        verbose_name="Estimated SOP",
    )
    """
    status = models.CharField(
        max_length=15, choices=ALLOWABLE_TYPES_PROJECT_STATUS, default=0
    )
    region = models.CharField(
        max_length=10, choices=ALLOWABLE_TYPES_REGION, default="EMEA"
    )
    secondRegion = models.CharField(
        max_length=10,
        choices=ALLOWABLE_TYPES_REGION,
        blank=True,
        null=True,
        verbose_name="Second Region",
    )

    dcChannel = models.CharField(
        max_length=12, choices=ALLOWABLE_TYPES_DCCHANNEL, blank=True, null=True
    )
    """

    status = models.ForeignKey(
        ProjectStatus, on_delete=models.SET_NULL, blank=True, null=True
    )
    region = models.ForeignKey(
        Regions, on_delete=models.PROTECT, blank=True, null=True)
    secondRegion = models.ForeignKey(
        SecondRegion, on_delete=models.PROTECT, blank=True, null=True
    )
    dcChannel = models.ForeignKey(
        DistributionChannels, on_delete=models.PROTECT, blank=True, null=True
    )

    valid = models.BooleanField(default=True, blank=True, null=True)
    mainCustomer = models.ForeignKey(
        MainCustomers,
        on_delete=models.PROTECT,
        blank=False,
        null=True,
        verbose_name="Main Customer",
    )

    finalCustomer = models.ForeignKey(
        FinalCustomers,
        on_delete=models.PROTECT,
        blank=False,
        null=True,
        verbose_name="Final Customer",
    )

    # chained foreign key removed after customer alignment
    """
    finalCustomer = ChainedForeignKey(
        FinalCustomers,
        chained_field="mainCustomer",
        chained_model_field="mainCust",
        verbose_name="Final Customer",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
    )
    """
    # salesName = models.ForeignKey(
    #     SalesName, on_delete=models.PROTECT, blank=True, null=True
    # )

    """
    product_family = models.ForeignKey(
        ProductFamily, on_delete=models.SET_NULL, null=True
    )
    product_series = ChainedForeignKey(
        ProductSeries,
        chained_field="product_family",
        chained_model_field="family",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
    )
    product_package = ChainedForeignKey(
        ProductPackage,
        chained_field="product_series",
        chained_model_field="series",
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
    )

    product = ChainedForeignKey(
        Product,
        chained_field="product_package",
        chained_model_field="package",
        show_all=False,
        auto_choose=False,
        sort=True,
        null=True,
    )
    """
    sales_name = models.ForeignKey(
        SalesName,
        on_delete=models.SET_NULL,
        null=True,
    )

    comment = models.TextField(blank=True, null=True)
    projectName = models.CharField(max_length=150, verbose_name="Project Name")
    syntheticProjectName = models.CharField(
        max_length=65, verbose_name="SyntheticProjectName", blank=True, null=True)
    projectDescription = models.CharField(
        max_length=400, default="", blank=True, null=True
    )
    draft = models.BooleanField(default=True)
    salesNameDefaulted = models.BooleanField(default=True)
    priceValidUntil = models.DateField(blank=True, null=True)

    priceType = models.ForeignKey(
        PriceStatus, on_delete=models.PROTECT, blank=True, null=True
    )
    """
    priceType = models.CharField(
        max_length=5, choices=ALLOWABLE_TYPES_PRICE_STATUS, blank=True, null=True
    )
    """

    # comment for Saadat: while entering data, if a distributor / ems / tier1 or OEM is not available on the dropdown list, the user should be able to create a new one on the fly
    distributor = models.ForeignKey(
        Distributors, on_delete=models.PROTECT, blank=True, null=True
    )
    ems = models.ForeignKey(
        EMS, on_delete=models.PROTECT, blank=True, null=True, verbose_name="EMS"
    )
    tier1 = models.ForeignKey(
        Tier1, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Tier 1"
    )
    oem = models.ForeignKey(
        OEM, on_delete=models.PROTECT, blank=True, null=True, verbose_name="OEM"
    )

    vpaCustomer = models.ForeignKey(
        VPACustomers,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="OEM",
    )  # models.BooleanField(default=False, blank=True, null=True)

    """
    salesContact = models.ForeignKey(
        SalesContacts,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name="Sales Contact",
    )
    """

    salesContact = models.CharField(max_length=30, blank=True, null=True)

    """
    salesOpportunity = models.ForeignKey(
        SalesOpportunities, on_delete=models.PROTECT, blank=True, null=True, verbose_name="salesopportunity"
    )
    """
    is_viewing = models.BooleanField(
        default=False, help_text="Checks if someone is viewing this project"
    )

    is_viewing_user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="is_viewing_user",
    )

    dummy = models.BooleanField(default=False)
    projectReviewed = models.BooleanField(default=False, blank=True, null=True)
    reviewDate = models.DateField(blank=True, null=True)
    modreason = models.CharField(max_length=15, blank=True, null=True)
    contractualCurrency = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self):
        return f"PRJ_FC_Uc_{self.id}_{self.mainCustomer}_{self.finalCustomer}_{self.applicationMain}_{self.applicationDetail}_{self.sales_name}"

    # unique constraint for a draft!
    # for transfer into BoUp or draft = False, the check has to be without user or draft.
    # this way, the combinaiton of MC + FC + AD + AM + SN is unique
    class Meta:
        constraints = [
            UniqueConstraint(
                fields=[
                    "mainCustomer",
                    "finalCustomer",
                    "draft",
                    "productMarketer",
                    "applicationDetail",
                    "applicationMain",
                    "sales_name",
                    "dummy",
                    "syntheticProjectName"
                ],
                name="unique_together_project",
            ),
        ]


class ProjectError(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    error_ids = models.CharField(max_length=100)

    def __str__(self):
        return f"Errors of {self.project.projectName}"

    def get_errors(self):
        from .helperFunctions import HighLevelProjectProblems
        error_ids = (int(x) for x in self.error_ids.split(","))
        # Remove duplicates
        error_ids = tuple(set(error_ids))
        errors = [HighLevelProjectProblems(error) for error in error_ids]
        return errors


class MissingOrders(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)


class MissingSalesPlan(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)


class OrdersWithNoProject(models.Model):
    rfp = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    mainCustomer = models.ForeignKey(
        MainCustomers, on_delete=models.CASCADE, blank=True, null=True
    )
    endCustomer = models.ForeignKey(
        FinalCustomers, on_delete=models.CASCADE, blank=True, null=True
    )


class SalesPlanWithNoProject(models.Model):
    rfp = models.ForeignKey(
        Product, on_delete=models.CASCADE, blank=True, null=True)
    mainCustomer = models.ForeignKey(
        MainCustomers, on_delete=models.CASCADE, blank=True, null=True
    )
    endCustomer = models.ForeignKey(
        FinalCustomers, on_delete=models.CASCADE, blank=True, null=True
    )


class ToDoItems(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    valid = models.BooleanField(default=True, blank=True, null=True)
    date = models.DateTimeField(auto_now=True)
    description = models.CharField(max_length=30, blank=True, null=True)
    dragonCodes = models.CharField(max_length=20, blank=True, null=True)
    source = models.CharField(max_length=10, blank=True, null=True)
